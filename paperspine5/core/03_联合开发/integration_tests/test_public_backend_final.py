"""Public backend regression tests with real temporary files/SQLite/ZIP bytes.

Review commands below are explicitly synthetic protocol fixtures, NOT an
independent scholarly review, real paper delivery, or browser acceptance.
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import stat
import struct
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from paperspine_figure_integration.p1_application import (
    DomainError, agent_execute, business_execute,
)
from paperspine_figure_integration.delivery_manifest import build_delivery_manifest
from paperspine_figure_integration.p2_facades import build_application, create_business_server, create_mcp_server
from paperspine_figure_integration.p7_artifact_import import verify_delivery_archive
from paperspine_figure_integration.product_kernel import ContractError


def zip_bytes(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, body in entries:
            archive.writestr(name, body)
    return stream.getvalue()


class PublicBackendFinalTests(unittest.TestCase):
    def test_configuration_change_retires_old_choice_and_replay_preserves_it(self):
        self.command('RequestDecision', {
            'decision_id': 'old-configuration-boundary', 'task_version': self.sequence,
            'decision_type': 'target_boundary', 'prompt': 'Old configuration fixture',
            'allowed_decisions': [{'option_id': 'keep', 'label': 'Keep'},
                                  {'option_id': 'change', 'label': 'Change'}],
            'scope_refs': ['configuration'],
            'requested_by_command_id': f'fixture-command-{self.sequence + 1}', 'expires_at': None,
        })
        self.command('SaveConfiguration', {'research_mode': 'required',
            'network_policy': {'allow_network': True, 'allow_external_upload': False}}, user=True)
        before = self.service.list_task_events('fixture')
        for projection in (self.service.event_store.projection('fixture'),
                           self.service.event_store.rebuild_projections()['fixture']):
            decision = projection['decisions'][0]
            self.assertEqual(decision['status'], 'pending')  # never forge a resolution
            self.assertTrue(decision['stale'])
            self.assertEqual(decision['stale_reason'], 'configuration_changed')
        self.assertEqual(self.service.list_task_events('fixture'), before)

        self.command('RequestDecision', {
            'decision_id': 'current-choice', 'task_version': self.sequence,
            'decision_type': 'motivation', 'prompt': 'Current fixture choice',
            'allowed_decisions': [{'option_id': 'chosen', 'label': 'Current option'}],
            'scope_refs': ['analysis'],
            'requested_by_command_id': f'fixture-command-{self.sequence + 1}', 'expires_at': None,
        })
        self.command('ResolveDecision', {'decision_id': 'current-choice', 'option_id': 'chosen',
            'reason': 'Protocol fixture selection.', 'confirmed_at': '2026-09-07T00:00:00Z'}, user=True)
        self.assertEqual(self.service.event_store.projection('fixture')['status'], 'open')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paperspine-backend-regression-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / 'core').mkdir()
        self.service, self.kernel = build_application(
            user_data_root=self.base / 'user', core_root=self.base / 'core',
            domain_database=self.base / 'events.db', contracts_root=ROOT / 'contracts')
        self.addCleanup(self.kernel.close)
        self.sequence = 0
        self.command('OpenTask', {'mode': 'open', 'title': 'Protocol fixture, not a scholarly paper'})
        self.workspace = Path(self.kernel.get_task('fixture')['workspace_root'])
        self.tex = b'\\documentclass{article}\n\\begin{document}Protocol fixture v1.\\end{document}\n'
        self.bib = b'% Protocol fixture: no scholarly references asserted.\n'
        self.figure = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Protocol fixture</text></svg>'
        self.publish('analysis', 'research_note', b'Existing analysis fixture; do not rerun.\n', 'analysis.md', 'research')
        self.publish('tex-v1', 'tex', self.tex, 'manuscript.tex')
        self.publish('bib', 'bibliography', self.bib, 'refs.bib')
        self.publish('figure-one', 'figure', self.figure, 'figure.svg', 'figure')

    def command(self, kind, payload, *, user=False, review_fixture=False):
        self.sequence += 1
        projection = self.service.event_store.projection('fixture') or {}
        request = {'schema_version': '1.1', 'command_id': f'fixture-command-{self.sequence}',
                   'task_id': 'fixture', 'expected_version': projection.get('task_version', 0), 'payload': payload}
        if user:
            return business_execute(self.service, request, principal_id='fixture-user',
                                    session_id='fixture-session', command_type=kind)
        return agent_execute(self.service, request,
                             principal_id='protocol-review-fixture' if review_fixture else 'fixture-host',
                             command_type=kind, reviewer=review_fixture)

    def publish(self, artifact_id, kind, body, filename, stage='draft', *, supersedes=None):
        path = self.workspace / 'paper' / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        return self.command('PublishArtifact', {'artifact_id': artifact_id, 'artifact_type': kind,
            'stage': stage, 'source': {'relative_path': 'paper/' + filename},
            **({'supersedes_artifact_ids': supersedes} if supersedes is not None else {})})

    def test_explicit_figure_replacement_preserves_other_panels_history_and_replay(self):
        self.ready_fixture()
        other = self.figure.replace(b'fixture', b'unaffected panel')
        corrected = self.figure.replace(b'fixture', b'corrected panel')
        self.publish('figure-two', 'figure', other, 'two.svg', 'figure')
        self.publish('figure-one-v2', 'figure', corrected, 'one-v2.svg', 'figure')
        self.assertFalse(next(a for a in self.service.get_task('fixture')['artifacts']
                              if a['artifact_id'] == 'figure-one').get('stale', False))
        # A replacement can be declared after the new bytes were first published.
        self.publish('figure-one-v2', 'figure', corrected, 'one-v2.svg', 'figure', supersedes=['figure-one'])
        current = self.service.get_task('fixture')
        artifacts = {a['artifact_id']: a for a in current['artifacts']}
        self.assertTrue(artifacts['figure-one']['stale'])
        self.assertEqual(artifacts['figure-one']['superseded_by'], 'figure-one-v2')
        self.assertEqual(artifacts['figure-one-v2']['supersedes_artifact_ids'], ['figure-one'])
        self.assertFalse(artifacts['figure-two'].get('stale', False))
        self.assertFalse(artifacts['analysis'].get('stale', False))
        self.assertTrue(artifacts['package-v1']['stale'])
        self.assertIn('figure-one', current['reviews'][0]['stale_artifact_ids'])
        with self.assertRaises(DomainError):
            self.service.read_artifact('fixture', 'figure-one')
        self.assertEqual(self.service.read_artifact('fixture', 'figure-one', allow_historical=True)[1], self.figure)
        ids = ['tex-v1', 'bib', 'figure-one-v2', 'figure-two']
        self.record_contract_review_fixture(ids)
        package = zip_bytes([('manuscript.tex', self.tex), ('refs.bib', self.bib),
                             ('one.svg', corrected), ('two.svg', other)])
        self.publish('corrected-package', 'delivery_package', package, 'corrected.zip', 'delivery')
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])
        self.publish('figure-one-v2', 'figure', corrected, 'one-v2.svg', 'figure', supersedes=['figure-one'])
        self.assertTrue(self.service.get_task('fixture')['delivery']['local_download_ready'])
        before = self.service.event_store.projection('fixture')
        self.assertEqual(self.service.event_store.rebuild_projections()['fixture'], before)

    def test_replacement_rejects_unknown_cross_task_self_and_different_type_before_import(self):
        agent_execute(self.service, {'schema_version': '1.1', 'command_id': 'open-other',
            'task_id': 'other', 'expected_version': 0, 'payload': {'mode': 'open', 'title': 'Other fixture'}},
            principal_id='fixture-host', command_type='OpenTask')
        root = Path(self.kernel.get_task('other')['workspace_root']) / 'paper'
        root.mkdir(exist_ok=True)
        (root / 'foreign.svg').write_bytes(self.figure)
        agent_execute(self.service, {'schema_version': '1.1', 'command_id': 'publish-other',
            'task_id': 'other', 'expected_version': 1, 'payload': {'artifact_id': 'foreign-figure',
            'artifact_type': 'figure', 'stage': 'figure', 'source': {'relative_path': 'paper/foreign.svg'}}},
            principal_id='fixture-host', command_type='PublishArtifact')
        before = self.service.list_task_events('fixture')
        registered = len(self.kernel.list_artifacts('fixture'))
        for replacement in ['missing', 'foreign-figure', 'new-figure', 'bib']:
            with self.subTest(replacement=replacement), self.assertRaisesRegex(DomainError, 'same type in this task'):
                self.publish('new-figure', 'figure', self.figure, 'new.svg', 'figure', supersedes=[replacement])
            self.assertEqual(self.service.list_task_events('fixture'), before)
            self.assertEqual(len(self.kernel.list_artifacts('fixture')), registered)

    def test_open_major_finding_prevents_delivery_even_with_complete_review_coverage(self):
        self.ready_fixture()
        self.command('SubmitReview', {'review_id': 'major-review-fixture',
            'reviewer_id': 'protocol-review-fixture',
            'reviewed_artifact_ids': ['analysis', 'tex-v1', 'bib', 'figure-one'],
            'findings': [{'finding_id': 'real-fix-required-fixture', 'severity': 'major',
                          'message': 'Protocol fixture for a required scientific correction.'}]}, review_fixture=True)
        current = self.service.get_task('fixture')
        self.assertEqual(current['status'], 'review_blocked')
        self.assertFalse(current['delivery']['local_download_ready'])
        before = self.service.list_task_events('fixture')
        with self.assertRaisesRegex(DomainError, 'major review findings remain open'):
            self.prepare()
        self.assertEqual(self.service.list_task_events('fixture'), before)

    def submit_finding_round(self, review_id, *finding_ids):
        return self.command('SubmitReview', {'review_id': review_id,
            'reviewer_id': 'protocol-review-fixture',
            'reviewed_artifact_ids': ['analysis', 'tex-v1', 'bib', 'figure-one'],
            'findings': [{'finding_id': finding_id, 'severity': 'major',
                          'message': f'{review_id}: correction {index}'}
                         for index, finding_id in enumerate(finding_ids, 1)]}, review_fixture=True)

    def resolution_payload(self, **extra):
        current = self.service.event_store.projection('fixture')
        return {'finding_id': 'F01', 'revision_id': str(current['task_version']),
                'resolution_artifact_ids': ['tex-v1'], 'explanation': 'Fixture correction.', **extra}

    def test_reused_finding_id_can_close_the_only_open_round_and_unblock_delivery(self):
        self.package('reviewed-package')
        self.submit_finding_round('review-1', 'F01')
        self.command('ResolveFinding', self.resolution_payload())
        self.submit_finding_round('review-2', 'F01')
        with self.assertRaisesRegex(DomainError, 'major review findings remain open'):
            self.prepare()

        self.command('ResolveFinding', self.resolution_payload())
        events = self.service.event_store.events('fixture')
        resolutions = [event['payload'] for event in events if event['event_type'] == 'finding.resolved']
        self.assertEqual([item['review_id'] for item in resolutions], ['review-1', 'review-2'])
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_ambiguous_finding_requires_scope_and_records_the_explicit_round(self):
        self.package('reviewed-package')
        for review_id in ('review-1', 'review-2'):
            self.submit_finding_round(review_id, 'F01')
        store = self.service.event_store
        before = store.events('fixture')
        current = store.projection('fixture')
        with self.assertRaises(DomainError) as caught:
            self.command('ResolveFinding', self.resolution_payload())
        error = caught.exception.value
        self.assertEqual(error['code'], 'validation_failed')
        self.assertEqual(error['details']['review_ids'], ['review-1', 'review-2'])
        self.assertEqual(error['details']['next_action'], 'specify_review_id')
        with self.assertRaises(DomainError) as caught:
            self.command('ResolveFinding', self.resolution_payload(review_id='unknown-review'))
        self.assertEqual(caught.exception.value['code'], 'not_found')
        with self.assertRaises(DomainError) as caught:
            self.command('ResolveFinding', self.resolution_payload(review_id='review-2', revision_id='1'))
        self.assertEqual(caught.exception.value['code'], 'version_conflict')
        with self.assertRaisesRegex(DomainError, 'unique within a review'):
            self.submit_finding_round('review-3', 'F01', 'F01')
        self.assertEqual(store.events('fixture'), before)

        expected = [{'review_id': review_id, 'finding_id': 'F01'} for review_id in ('review-1', 'review-2')]
        manifest = build_delivery_manifest(current)
        self.assertEqual(manifest['open_blocking_findings'], expected)
        self.assertFalse(manifest['checks']['blocking_findings_closed'])
        check = self.service.check_delivery({'task_id': 'fixture', 'package_path': 'paper/reviewed-package.zip',
                                             'required_formats': ['tex', 'bibliography', 'figures']})
        self.assertEqual([{key: item[key] for key in ('review_id', 'finding_id')}
                          for item in check['open_findings']], expected)

        result = self.command('ResolveFinding', self.resolution_payload(review_id='review-2'))
        self.assertEqual([item['status'] for item in result['projection']['findings']], ['open', 'resolved'])
        # An explicit retry of the already closed round cannot affect another round.
        with self.assertRaises(DomainError) as caught:
            self.command('ResolveFinding', self.resolution_payload(review_id='review-2'))
        self.assertEqual(caught.exception.value['code'], 'idempotency_conflict')
        self.command('ResolveFinding', self.resolution_payload())
        self.assertEqual(store.events('fixture')[-1]['payload']['review_id'], 'review-1')
        resolved = store.projection('fixture')
        self.assertEqual(store.rebuild_projections()['fixture'], resolved)
        with self.assertRaises(DomainError) as caught:
            self.command('ResolveFinding', self.resolution_payload())
        self.assertEqual(caught.exception.value['code'], 'idempotency_conflict')
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_mcp_and_http_accept_explicit_review_scope(self):
        self.submit_finding_round('review-1', 'F01')
        self.submit_finding_round('review-2', 'F01')
        store = self.service.event_store

        async def close_with_mcp():
            server = create_mcp_server(self.service, principal_id='fixture-host')
            name = 'paperspine_resolve_finding'
            tool = next(tool for tool in await server.list_tools() if tool.name == name)
            schema = tool.input_schema['properties']['request']['properties']['payload']
            self.assertIn('review_id', schema['properties'])
            self.assertNotIn('review_id', schema['required'])
            request = {'schema_version': '1.1', 'task_id': 'fixture', 'command_id': 'mcp-close',
                       'expected_version': store.projection('fixture')['task_version'],
                       'payload': self.resolution_payload(review_id='review-2')}
            response = await server.call_tool(name, {'request': request})
            result = response.structured_content
            self.assertNotIn('error', result)
            self.assertEqual([item['status'] for item in result['projection']['findings']], ['open', 'resolved'])

        asyncio.run(close_with_mcp())
        with create_business_server(self.service, principal_id='fixture-user', session_id='fixture-session') as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                payload = self.resolution_payload(review_id='review-1')
                del payload['revision_id']  # The 1.0 HTTP request shape still works.
                request = {'schema_version': '1.0', 'command_id': 'http-close',
                           'expected_version': store.projection('fixture')['task_version'], 'payload': payload}
                url = f'http://127.0.0.1:{server.server_port}/api/v1/tasks/fixture/findings/F01/resolution'
                with urlopen(Request(url, data=json.dumps(request).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'}), timeout=5) as response:
                    result = json.load(response)
            finally:
                server.shutdown()
                thread.join(timeout=5)
        self.assertEqual([item['status'] for item in result['projection']['findings']], ['resolved', 'resolved'])
        self.assertEqual(store.events('fixture')[-1]['payload']['review_id'], 'review-1')

    def test_legacy_hotfix_events_keep_later_rounds_resolved_on_rebuild(self):
        self.package('reviewed-package')
        store = self.service.event_store

        def append_legacy_resolution(label):
            events = store.events('fixture')
            latest = events[-1]
            command_id = 'legacy-' + label
            event = {**latest, 'event_type': 'finding.resolved', 'actor': events[0]['actor'],
                     'command_id': command_id, 'event_id': command_id + '-event',
                     'sequence': latest['sequence'] + 1, 'task_version': latest['task_version'] + 1,
                     'payload': {'payload_type': 'finding.resolved', **self.resolution_payload(explanation=label)}}
            store.append({'command_id': command_id, 'task_id': 'fixture'}, event, {})

        self.submit_finding_round('review-1', 'F01')
        append_legacy_resolution('original')
        append_legacy_resolution('legacy-repeat')
        self.submit_finding_round('review-2', 'F01')
        self.submit_finding_round('review-3', 'F01')
        append_legacy_resolution('hotfix-2')
        append_legacy_resolution('hotfix-3')
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

        before = store.events('fixture')
        rebuilt = store.rebuild_projections()['fixture']
        self.assertEqual([(item['review_id'], item['status'], item['explanation'])
                          for item in rebuilt['findings']],
                         [('review-1', 'resolved', 'legacy-repeat'), ('review-2', 'resolved', 'hotfix-2'),
                          ('review-3', 'resolved', 'hotfix-3')])
        self.assertTrue(rebuilt['delivery']['local_download_ready'])
        self.assertEqual(store.events('fixture'), before)

    def record_contract_review_fixture(self, ids):
        return self.command('SubmitReview', {'review_id': f'protocol-fixture-{self.sequence}',
            'reviewer_id': 'protocol-review-fixture', 'reviewed_artifact_ids': ids, 'findings': []}, review_fixture=True)

    def prepare(self):
        return self.command('PrepareDelivery', {'scope': 'local_delivery',
                                               'required_formats': ['tex', 'bibliography', 'figures']})

    def package(self, name, tex=None):
        body = zip_bytes([('paper/manuscript.tex', self.tex if tex is None else tex),
                          ('paper/refs.bib', self.bib), ('paper/figures/one.svg', self.figure)])
        self.publish(name, 'delivery_package', body, name + '.zip', 'delivery')
        return body

    def ready_fixture(self):
        self.record_contract_review_fixture(['analysis', 'tex-v1', 'bib', 'figure-one'])
        self.package('package-v1')
        return self.prepare()

    def test_old_zip_with_new_reviewed_manuscript_is_rejected_without_delivery_event(self):
        original = self.ready_fixture()
        old_body = self.service.read_artifact('fixture', 'package-v1')[1]
        revised = self.tex.replace(b'v1', b'v2: revised text')
        self.publish('tex-v2', 'tex', revised, 'revised.tex')
        current = self.service.get_task('fixture')
        self.assertFalse(current['delivery']['local_download_ready'])
        self.assertTrue(next(a for a in current['artifacts'] if a['artifact_id'] == 'tex-v1')['stale'])
        self.assertFalse(next(a for a in current['artifacts'] if a['artifact_id'] == 'analysis').get('stale', False))
        self.assertEqual(current['delivery_history'][0]['task_version'], original['task_version'])
        self.assertEqual(self.service.read_artifact('fixture', 'tex-v1', allow_historical=True)[1], self.tex)
        self.record_contract_review_fixture(['tex-v2'])
        self.publish('old-zip-republished', 'delivery_package', old_body, 'old.zip', 'delivery')
        before = len(self.service.list_task_events('fixture'))
        with self.assertRaisesRegex(DomainError, 'current required outputs: tex-v2') as caught:
            self.prepare()
        self.assertEqual(caught.exception.value['code'], 'validation_failed')
        self.assertEqual(len(self.service.list_task_events('fixture')), before)
        self.assertEqual(self.service.read_artifact('fixture', 'package-v1', allow_historical=True)[1], old_body)
        self.assertFalse(self.service.get_task('fixture')['delivery']['local_download_ready'])

    def test_current_package_passes_and_restore_preserves_workspace_and_history(self):
        self.ready_fixture()
        revised = self.tex.replace(b'v1', b'v2')
        self.publish('tex-v2', 'tex', revised, 'revised.tex')
        self.record_contract_review_fixture(['tex-v2'])
        body = self.package('package-v2', revised)
        result = self.prepare()
        self.assertTrue(result['projection']['delivery']['local_download_ready'])
        self.assertFalse(result['projection']['delivery']['submission_ready'])
        self.assertEqual(result['projection']['delivery']['package_artifact_id'], 'package-v2')
        self.assertEqual(self.service.read_artifact('fixture', 'package-v2')[1], body)
        before = self.service.event_store.projection('fixture')
        self.assertEqual(self.service.event_store.rebuild_projections()['fixture'], before)
        restored, kernel = build_application(user_data_root=self.base / 'user', core_root=self.base / 'core',
            domain_database=self.base / 'events.db', contracts_root=ROOT / 'contracts')
        try:
            snapshot = restored.get_task('fixture')
            self.assertEqual(snapshot['workspace_root'], str(self.workspace))
            self.assertTrue(snapshot['delivery']['local_download_ready'])
            self.assertEqual(len(snapshot['delivery_history']), 1)
            self.assertEqual(restored.read_artifact('fixture', 'package-v1', allow_historical=True)[1],
                             self.service.read_artifact('fixture', 'package-v1', allow_historical=True)[1])
        finally:
            kernel.close()

    def test_empty_zip_and_changed_registered_bytes_cannot_pass(self):
        self.record_contract_review_fixture(['tex-v1', 'bib', 'figure-one'])
        self.publish('empty-package', 'delivery_package', zip_bytes([]), 'empty.zip', 'delivery')
        with self.assertRaisesRegex(DomainError, 'current required outputs'):
            self.prepare()
        self.package('good-package')
        path = self.service.legacy_adapter.artifact_path('fixture', 'tex-v1')
        path.write_bytes(self.tex + b'% unreviewed edit\n')
        version = self.service.event_store.projection('fixture')['task_version']
        with self.assertRaises(DomainError) as caught:
            self.prepare()
        self.assertEqual(caught.exception.value['code'], 'validation_failed')
        self.assertEqual(self.service.event_store.projection('fixture')['task_version'], version)
        self.assertFalse(self.service.event_store.projection('fixture').get('recovery'))
        self.assertFalse(self.service.get_task('fixture').get('delivery'))
        self.publish('repaired-tex', 'tex', self.tex, 'repaired.tex')
        self.record_contract_review_fixture(['repaired-tex'])
        self.package('repaired-package')
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_draft_milestone_invalidates_review_and_delivery_but_keeps_other_work(self):
        self.ready_fixture()
        kernel_revision = self.kernel.get_task('fixture')['revision']
        self.command('CommitMilestone', {'stage': 'draft', 'summary': 'A textual revision needs review.',
                                         'artifact_ids': ['tex-v1']})
        current = self.service.get_task('fixture')
        self.assertFalse(current['delivery']['local_download_ready'])
        self.assertEqual(set(current['reviews'][0]['stale_artifact_ids']), {'tex-v1', 'bib'})
        self.assertFalse(any(a.get('stale') for a in current['artifacts']))
        self.assertEqual(self.kernel.get_task('fixture')['revision'], kernel_revision)
        with self.assertRaisesRegex(DomainError, 'independent review'):
            self.prepare()
        self.record_contract_review_fixture(['tex-v1', 'bib'])
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_feedback_scope_preserves_analysis_and_unaffected_review_coverage(self):
        self.ready_fixture()
        kernel_revision = self.kernel.get_task('fixture')['revision']
        for scope, affected, stage in [('manuscript', {'tex-v1', 'bib'}, 'draft'),
                                       ('figures', {'figure-one', 'tex-v1'}, 'figure'),
                                       ('figure_mapping', {'figure-one', 'tex-v1'}, 'figure'),
                                       ('all', {'analysis', 'tex-v1', 'bib', 'figure-one'}, 'draft')]:
            with self.subTest(scope=scope):
                self.record_contract_review_fixture(['analysis', 'tex-v1', 'bib', 'figure-one'])
                self.command('RequestRevision', {'scope': scope, 'feedback': 'Protocol feedback fixture.'}, user=True)
                current = self.service.get_task('fixture')
                self.assertEqual(current['stage'], stage)
                self.assertEqual(set(current['reviews'][-1]['stale_artifact_ids']), affected)
                self.assertFalse(any(a.get('stale') for a in current['artifacts']))
                self.assertEqual(self.kernel.get_task('fixture')['revision'], kernel_revision)
                self.assertEqual(self.service.read_artifact('fixture', 'analysis')[1],
                                 b'Existing analysis fixture; do not rerun.\n')
                with self.assertRaisesRegex(DomainError, 'independent review'):
                    self.prepare()

    def test_republishing_identical_bytes_and_review_milestone_keep_valid_review(self):
        self.ready_fixture()
        self.publish('tex-v1', 'tex', self.tex, 'manuscript.tex')
        self.assertTrue(self.service.get_task('fixture')['delivery']['local_download_ready'])
        self.command('CommitMilestone', {'stage': 'review', 'summary': 'Protocol review bookkeeping only.',
                                         'artifact_ids': ['tex-v1']})
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_review_coverage_requires_exact_current_hash(self):
        self.ready_fixture()
        current = self.service.event_store.projection('fixture')
        current['reviews'][0]['reviewed_hashes']['tex-v1'] = '0' * 64
        with self.assertRaisesRegex(DomainError, 'independent review'):
            self.service._event_for_public_command('PrepareDelivery',
                {'scope': 'local_delivery', 'required_formats': ['tex']}, current)

    def test_new_figure_preserves_other_panels_and_rechecks_rendered_manuscript(self):
        self.ready_fixture()
        second = self.figure.replace(b'Protocol fixture', b'Second panel fixture')
        self.publish('figure-two', 'figure', second, 'second.svg', 'figure')
        current = self.service.get_task('fixture')
        self.assertEqual(current['reviews'][0]['stale_artifact_ids'], ['tex-v1'])
        self.assertEqual({a['artifact_id'] for a in current['artifacts'] if a.get('stale')}, {'package-v1'})
        self.assertFalse(current['delivery']['local_download_ready'])
        self.record_contract_review_fixture(['tex-v1', 'figure-two'])
        self.package('incomplete-package')
        with self.assertRaisesRegex(DomainError, 'current required outputs: figure-two'):
            self.prepare()
        body = zip_bytes([('manuscript.tex', self.tex), ('refs.bib', self.bib),
                          ('one.svg', self.figure), ('two.svg', second)])
        self.publish('package-two-figures', 'delivery_package', body, 'two-figures.zip', 'delivery')
        self.assertTrue(self.prepare()['projection']['delivery']['local_download_ready'])

    def test_archive_variants_coexist_until_paper_bytes_change_and_replay_keeps_history(self):
        self.record_contract_review_fixture(['tex-v1', 'bib', 'figure-one'])
        share = self.package('share-package')
        workspace = zip_bytes([('paper/manuscript.tex', self.tex), ('paper/refs.bib', self.bib),
                               ('paper/figures/one.svg', self.figure), ('paper/README.md', b'Editable source fixture')])
        self.publish('workspace-package', 'delivery_package', workspace, 'workspace.zip', 'delivery')
        self.prepare()
        events = self.service.list_task_events('fixture')
        for projection in (self.service.event_store.projection('fixture'),
                           self.service.event_store.rebuild_projections()['fixture']):
            self.assertEqual({a['artifact_id'] for a in projection['artifacts']
                              if a['artifact_type'] == 'delivery_package' and not a.get('stale')},
                             {'share-package', 'workspace-package'})
        self.assertEqual(self.service.list_task_events('fixture'), events)
        self.assertEqual(self.service.read_artifact('fixture', 'share-package')[1], share)
        self.assertEqual(self.service.read_artifact('fixture', 'workspace-package')[1], workspace)
        self.publish('tex-revised', 'tex', self.tex.replace(b'v1', b'v2'), 'revised.tex')
        packages = [a for a in self.service.get_task('fixture')['artifacts'] if a['artifact_type'] == 'delivery_package']
        self.assertTrue(all(a['stale'] and a['stale_reason'] == 'packaged_outputs_changed' for a in packages))
        self.record_contract_review_fixture(['tex-revised'])
        with self.assertRaisesRegex(DomainError, 'fresh delivery package'):
            self.prepare()
        self.assertEqual(self.service.read_artifact('fixture', 'share-package', allow_historical=True)[1], share)
        self.assertEqual(self.service.read_artifact('fixture', 'workspace-package', allow_historical=True)[1], workspace)


class DeliveryArchiveSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='paperspine-archive-regression-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'package.zip'
        self.body = b'Current required protocol fixture bytes.'
        self.required = [{'artifact_id': 'current', 'sha256': hashlib.sha256(self.body).hexdigest()}]

    def check(self, body):
        self.path.write_bytes(body)
        verify_delivery_archive(self.path, self.required)

    def test_safe_nested_members_and_all_current_bytes_pass(self):
        self.check(zip_bytes([('paper/', b''), ('paper/current.tex', self.body), ('README.txt', b'Fixture')]))

    def test_unsafe_paths_duplicate_aliases_and_links_fail(self):
        for name in ('../escape', '/absolute', 'C:/escape', 'a/../b', 'a//b', 'a//',
                     'a./b', 'file:stream', 'NUL.txt', 'a/COM1.tex'):
            with self.subTest(name=name), self.assertRaises(ContractError):
                self.check(zip_bytes([('current.tex', self.body), (name, b'unsafe')]))
        # Windows ZipInfo normalizes backslashes at write time; mutate both
        # stored names to test the actual hostile archive, not the writer.
        with self.assertRaises(ContractError):
            self.check(zip_bytes([('current.tex', self.body), ('a/b', b'unsafe')]).replace(b'a/b', b'a\\b'))
        with self.assertRaises(ContractError):
            self.check(zip_bytes([('CURRENT.tex', self.body), ('current.tex', self.body)]))
        link = zipfile.ZipInfo('link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(ContractError):
            self.check(zip_bytes([('current.tex', self.body), (link, b'elsewhere')]))

    def test_crc_is_checked_even_for_nonrequired_members(self):
        archive = bytearray(zip_bytes([('extra.txt', b'corrupt-me'), ('current.tex', self.body)]))
        start = archive.index(b'corrupt-me')
        archive[start] ^= 1
        with self.assertRaisesRegex(ContractError, 'damaged or unreadable'):
            self.check(archive)

    def test_member_count_and_expanded_size_limits_fail(self):
        with self.assertRaisesRegex(ContractError, 'safe inspection limits'):
            self.check(zip_bytes([(f'{i}.txt', b'') for i in range(4097)]))
        archive = bytearray(zip_bytes([('current.tex', self.body)]))
        central = archive.index(b'PK\x01\x02')
        struct.pack_into('<I', archive, central + 24, 512 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ContractError, 'safe inspection limits'):
            self.check(archive)

    def test_invalid_deflate_is_a_validation_error(self):
        archive = bytearray(zip_bytes([('current.tex', b'\x07invalid-deflate')]))
        central = archive.index(b'PK\x01\x02')
        struct.pack_into('<H', archive, 8, zipfile.ZIP_DEFLATED)
        struct.pack_into('<H', archive, central + 10, zipfile.ZIP_DEFLATED)
        with self.assertRaisesRegex(ContractError, 'damaged or unreadable'):
            self.check(archive)


class DeliveryManifestDecisionTests(unittest.TestCase):
    def test_stale_pending_is_ignored_but_current_pending_still_blocks(self):
        from paperspine_figure_integration.delivery_manifest import build_delivery_manifest

        historical = {'decision_id': 'historical-choice', 'status': 'pending', 'stale': True}
        current = {'decision_id': 'current-choice', 'status': 'pending'}
        self.assertEqual([
            build_delivery_manifest({'decisions': decisions})['checks']['user_choices_resolved']
            for decisions in ([historical], [historical, current])
        ], [True, False])


if __name__ == '__main__':
    unittest.main()
