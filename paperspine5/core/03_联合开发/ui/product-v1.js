'use strict';
/* Thin Web client. Integration routes: /product-v1.{js,css}, existing task REST,
 * POST /api/v1/tasks/{id}/configuration (schema 1.1, patch payload with formats),
 * POST materials (schema 1.1). Projection: configuration, material_grants,
 * material_inventory.entries/grants/scan_issues and skill_bridge workflow files.
 * The bridge is derived from the same event projection and is read by the host
 * PaperSpine Skill as the Web-facing handoff.
 */
const $ = selector => document.querySelector(selector);
const id = new URLSearchParams(location.search).get('task_id');
const taskUrl = id ? `/api/v1/tasks/${encodeURIComponent(id)}` : null;
const pending = new Map();
const inFlight = new Set();
const dirtyConfig = new Set();
let latest = null;
let renderedVersion = null;
let renderedInventory = null;
let configLoaded = false;
const stageNames = {intake:'材料与设置',research:'研究',contribution:'动机与贡献',evidence:'证据',draft:'稿件',figure:'图件',review:'审核',delivery:'本地交付'};
const configDefaults = {workflow:'build_from_materials',scene:'journal',requested_scope:'local_delivery',target:{status:'unknown',name:null},output_language:'en',formats:['pdf','docx','tex'],network_policy:{allow_network:false,allow_external_upload:false},privacy:{allow_external_processing:false},author_voice_restoration:'off',budget:{time_minutes:null,token_limit:null,cost_limit:null}};
const configFields = {workflow:'#workflow',scene:'#scene',requested_scope:'#requested-scope',target:'#target-status',output_language:'#output-language',formats:'#deliverable-pdf',network_policy:'#allow-network',privacy:'#allow-external-processing',author_voice_restoration:'#author-voice-restoration',budget:'#budget-time'};

function notice(message, area = null, error = true) {
  const global = $('#operation-message');
  global.textContent = message; global.hidden = !message;
  global.classList.toggle('error', error);
  if (area) { area.textContent = message; area.classList.toggle('error', error); }
}
function clearNotice() { $('#operation-message').hidden = true; $('#operation-message').textContent = ''; }
function node(tag, text, className) { const n = document.createElement(tag); n.textContent = text; if (className) n.className = className; return n; }
function areaFor(key) { return key === 'materials' ? $('#material-message') : key === 'additional-materials' ? $('#additional-material-message') : key === 'configuration' ? $('#config-message') : null; }
function lockForm(key, locked) {
  const form = key === 'materials' ? $('#materials-form') : key === 'additional-materials' ? $('#additional-materials-form') : key === 'configuration' ? $('#config-form') : key === 'create' ? $('#create-form') : null;
  if (form) for (const control of form.querySelectorAll('input,select,button')) {
    if (control.id.startsWith('retry-')) continue;
    control.disabled = locked;
  }
  if (key === 'configuration' && !locked) updateTarget();
  if (key === 'create' && locked && !inFlight.has(key)) {
    const button = $('#create-form button'); button.disabled = false; button.textContent = '核对并重试原创建请求';
  }
  const retry = $(`#retry-${key}`);
  if (retry) retry.hidden = !pending.has(key);
}
function clearPending(key) { pending.delete(key); lockForm(key, false); }
function updateTarget() { $('#target-name').disabled = $('#target-status').value !== 'known'; $('#target-name').required = $('#target-status').value === 'known'; }
function isKnownRejection(error) {
  return ['validation_failed','version_conflict','idempotency_conflict','not_found','unsupported_schema_version','decision_already_resolved'].includes(error?.code);
}
async function jsonRequest(url, body) {
  const response = await fetch(url, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  let value;
  try { value = await response.json(); } catch (_) { throw new Error('未收到可核对的服务响应。'); }
  if (!response.ok && !value.error) throw new Error('服务未返回可核对的操作结果。');
  return value;
}
async function mutation(key, url, body) {
  if (inFlight.has(key)) return false;
  inFlight.add(key); pending.set(key, {url,body}); lockForm(key,true);
  try {
    const result = await jsonRequest(url,body);
    if (result.error) {
      if (isKnownRejection(result.error)) clearPending(key);
      notice(result.error.message || '请求被拒绝，请检查输入。',areaFor(key));
      await refreshTask();
      return false;
    }
    clearPending(key); clearNotice();
    if (key === 'configuration') dirtyConfig.clear();
    if (result.projection) render(result.projection);
    if (key === 'create') location.href = '/?task_id='+encodeURIComponent(result.task_id);
    if (key === 'materials') notice('材料已授权在本机只读使用，文件清单已更新。',areaFor(key),false);
    if (key === 'configuration') notice('设置已保存。',areaFor(key),false);
    return true;
  } catch (_) {
    notice('连接中断，执行结果尚未核对。请保留当前页面，核对并重试原请求；不要另建或改写请求。',areaFor(key));
    return false;
  } finally {
    inFlight.delete(key);
    lockForm(key,pending.has(key));
  }
}
async function retry(key) {
  const saved = pending.get(key);
  if (saved) await mutation(key,saved.url,saved.body);
}
async function refreshTask() {
  if (!taskUrl) return null;
  try {
    const value = await jsonRequest(taskUrl);
    if (value.error) {
      $('#status').textContent = value.error.message || '无法读取任务。';
      return null;
    }
    if (latest && value.task_version < latest.task_version) return latest;
    render(value);
    loadEvents(value.task_id);
    $('#status').textContent = value.recovery ? '需要继续论文工作' : '已连接论文任务';
    return value;
  } catch (_) {
    $('#status').textContent = '连接中断，已保存的论文仍会保留。';
    $('#recovery-card').hidden = false;
    $('#recovery-message').textContent = '请重新连接，读取同一任务的最新进度。';
    const b = $('#continue-work'); b.textContent = '重新连接'; b.disabled = false; b.onclick = refreshTask;
    return null;
  }
}
function render(value) {
  latest = value;
  const effectiveStage = value.effective_stage || value.stage;
  document.body.dataset.taskId = value.task_id;
  $('#task').textContent = JSON.stringify(value,null,2);
  $('#materials-card').hidden = false; $('#configuration-card').hidden = false;
  $('#additional-materials-card').hidden = false;
  $('#overview-card').hidden = false;
  for(const section of document.querySelectorAll('.task-only')) section.hidden=false;
  $('#task-title').textContent = value.title || '论文任务';
  $('#task-description').textContent = value.description || `围绕“${value.title || '论文任务'}”的 PaperSpine 论文任务`;
  $('#task-identity').textContent = `任务识别码：${value.task_id}`;
  $('#task-reference').textContent = `任务编号：${value.task_id}。请保存当前网址以便恢复。`;
  renderConfiguration(value);
  applyStageEditPolicy(value);
  const config=value.configuration;
  $('#host-handoff').value=`请使用 PaperSpine Skill，继续同一个论文任务 ${value.task_id}。\n工作台：${location.origin}/?task_id=${encodeURIComponent(value.task_id)}\n先通过当前服务/宿主接口读取最新任务、材料清单、配置和待办，不另建任务，不覆盖已有决定与文件。\n${config ? `已存配置：${config.target?.name||'目标待研究'}；${config.output_language}；${(config.formats||[]).join('、')}。以接口最新值为准。` : '任务配置尚未保存，请先与用户核对；不要假定期刊或输出要求。'}\n沿当前阶段继续研究、写作、作图与独立审核，真实产物和需要用户确认的选择写回本任务。不要把历史下载文件当作当前审核通过。`;
  const inventoryKey=JSON.stringify([value.material_inventory?.snapshot_sha256,value.material_inventory?.entries?.length,value.material_grants]);
  if(renderedInventory!==inventoryKey){renderedInventory=inventoryKey;renderInventory(value);filterMaterials();}
  showRecovery(value);
  renderDeliveryManifest(value);
  renderWorkflowFiles(value);
  const viewKey=JSON.stringify([value.task_version,value.legacy_runner?.revision,value.legacy_runner?.stage,(value.artifacts||[]).map(a=>[a.artifact_id,a.freshness,a.bytes_verified])]);
  if (renderedVersion === viewKey) return;
  renderedVersion = viewKey;
  const openFindings=(value.findings||[]).filter(f=>f.status==='open'), pendingChoices=(value.decisions||[]).filter(d=>d.status==='pending');
  $('#task-next-step').textContent = !value.material_grants?.length ? '下一步：提供本篇论文需要的材料。' : !value.configuration || value.configuration_stale ? '下一步：核对材料后保存论文任务设置，明确目标期刊、语言与输出格式。' : pendingChoices.length ? `下一步：完成 ${pendingChoices.length} 项需要你确认的选择。` : openFindings.length ? `下一步：处理 ${openFindings.length} 项审核问题，再核对新的交付物。` : '材料与设置已保存；请由宿主 Agent 在同一任务继续研究与写作。';
  const counts=$('#task-counts');counts.replaceChildren();
  for(const text of [`${value.material_inventory?.entries?.length||0} 个材料文件`,value.configuration?'配置已保存':'配置待保存',`${(value.artifacts||[]).length} 个成果记录`,`${openFindings.length} 个待处理问题`])counts.appendChild(node('span',text));
  const revisionAllowed=value.legacy_runner?.stage==='target_package_ready';
  $('#revision-request-submit').disabled=!revisionAllowed;
  $('#revision-availability').textContent=revisionAllowed?'可对当前已完成的本地版本提出修改；旧版本会保留。':'当前论文尚未完成本地交付。先完成材料配置、写作与审核；之后可在此提交下一轮修改意见。';
  const stages = $('#stages'); stages.replaceChildren();
  for (const [key,label] of Object.entries(stageNames)) stages.appendChild(node('li',label,key===effectiveStage?'active':null));
  const stale = value.delivery?.stale || value.configuration_stale;
  const mismatch = value.stage_mismatch ? '（已按执行引擎状态校正显示）' : '';
  $('#stage-copy').textContent = stale ? `材料或设置已变化，保留的成果需要重新核对。${mismatch}` : value.delivery_manifest?.ready ? `本地论文包已准备好；投稿仍需单独确认。${mismatch}` : `当前：${stageNames[effectiveStage] || '处理中'}${mismatch}`;
  const artifacts = $('#artifacts'); artifacts.replaceChildren();
  const currentFiles=node('div',''), historicalFiles=node('details','');historicalFiles.appendChild(node('summary','历史文件与先前版本'));
  for (const a of value.artifacts || []) {
    const row = node('div','', 'artifact'); const label = (a.filename || a.file_name || a.artifact_type || '文件');
    const link = node('a',label); link.href = a.download_url || `${taskUrl}/artifacts/${encodeURIComponent(a.artifact_id)}/download`; row.appendChild(link);
    row.appendChild(node('span',` · ${a.artifact_type}${a.size_bytes===undefined?'':' · '+formatSize(a.size_bytes)}`,'muted'));
    if (a.previewable && a.content_url) {const preview=node('a','打开预览','preview-link');preview.href=a.content_url;preview.target='_blank';preview.rel='noopener';row.appendChild(preview);}
    if (a.historical || a.freshness === 'stale' || a.stale) row.appendChild(node('span',' · 历史版本/需重新核对','muted'));
    if (a.stale) row.appendChild(node('span','（保留的成果，需重新核对）','muted'));
    (a.historical||a.stale?historicalFiles:currentFiles).appendChild(row);
  }
  artifacts.appendChild(currentFiles);if(historicalFiles.children.length>1)artifacts.appendChild(historicalFiles);
  renderFigures(value);
  if (!(value.artifacts || []).length) artifacts.appendChild(node('p','尚无可读文件。','muted'));
  const findings = $('#findings'); findings.replaceChildren();const resolved=node('details','');resolved.appendChild(node('summary','查看已处理审核记录'));
  for (const f of value.findings || []) {
    const row = node('div','', 'finding');
    row.appendChild(node('span',`${f.status==='resolved'?'已修复':'待修复'}：${f.message}`));
    if (f.status !== 'resolved') {
      row.appendChild(node('small',`修回必须由独立审核身份提交，并绑定当前论文修订 ${value.legacy_runner?.revision ?? '—'} 的新产物证据。`,'muted'));
    }
    (f.status==='resolved'?resolved:findings).appendChild(row);
  }
  if(resolved.children.length>1)findings.appendChild(resolved);
  if (!(value.findings || []).length) findings.appendChild(node('p','尚无审核问题。','muted'));
  showDecisions(value);
}
function applyStageEditPolicy(value) {
  const runnerStage=value.legacy_runner?.stage||'';
  const intakeStages=new Set(['uninitialized','awaiting_materials','awaiting_configuration']);
  const editable=!value.configuration || value.configuration_stale || intakeStages.has(runnerStage) || (value.effective_stage||value.stage)==='intake';
  const configForm=$('#config-form'), save=$('#save-configuration'), note=$('#config-readonly-note');
  if(configForm){for(const control of configForm.querySelectorAll('input,select,textarea,button')){if(control.id!=='retry-configuration')control.disabled=!editable;}configForm.dataset.readonly=editable?'false':'true';}
  if(save)save.hidden=!editable;
  if(note)note.hidden=editable;
  const materialsForm=$('#materials-form');
  if(materialsForm){const materialEditable=intakeStages.has(runnerStage)||(value.effective_stage||value.stage)==='intake';for(const control of materialsForm.querySelectorAll('input,select,textarea,button')){if(control.id!=='retry-materials')control.disabled=!materialEditable;}}
  const additional=$('#additional-materials-form');
  if(additional){const materialEditable=intakeStages.has(runnerStage)||(value.effective_stage||value.stage)==='intake';for(const control of additional.querySelectorAll('input,select,textarea,button'))control.disabled=!materialEditable;}
}
async function runnerControl(action){
  const status=$('#runner-control-status'), revision=Number($('#runner-controls-card')?.dataset.revision);
  if(!Number.isInteger(revision)){status.textContent='当前任务还没有可用的 Runner 修订，请先保存材料与设置。';return;}
  const key=`runner-${action}`; if(inFlight.has(key))return;
  inFlight.add(key); pending.set(key,{url:`${taskUrl}/runner/${action}`,body:null}); lockRunnerControls(true); status.textContent='正在核对当前修订…';
  try{const fresh=await refreshTask();if(!fresh||!Number.isInteger(fresh.legacy_runner?.revision))throw Error();const body={schema_version:'1.1',command_id:`web-runner-${action}-`+crypto.randomUUID(),expected_revision:fresh.legacy_runner.revision};const result=await jsonRequest(`${taskUrl}/runner/${action}`,body);if(result.error){status.textContent=result.error.message||'流程操作未执行。';return;}pending.delete(key);status.textContent=action==='bootstrap'?'论文流程已初始化。':'已请求从当前阶段继续。';await refreshTask();}catch(_){status.textContent='流程请求结果尚未核对，请刷新同一任务后再决定是否重试。';}finally{inFlight.delete(key);pending.delete(key);lockRunnerControls(false);}
}
function lockRunnerControls(locked){for(const id of ['#runner-bootstrap','#runner-resume']){const button=$(id);if(button)button.disabled=locked||!Number.isInteger(Number($('#runner-controls-card')?.dataset.revision));}}
async function loadEvents(taskId){
  const list=$('#events'); if(!list||!taskId)return;
  try{const value=await jsonRequest(`/api/v1/tasks/${encodeURIComponent(taskId)}/events`);const events=value.events||[];list.replaceChildren();if(!events.length){list.appendChild(node('li','暂无事件记录。','muted'));return;}for(const event of events.slice(-80).reverse()){const li=document.createElement('li');const when=event.occurred_at||event.created_at||'';if(when){const time=document.createElement('time');time.dateTime=when;time.textContent=new Date(when).toLocaleString();li.appendChild(time);}li.appendChild(node('code',event.event_type||event.type||'event'));if(event.command_id)li.appendChild(node('span',` · ${event.command_id}`,'muted'));list.appendChild(li);}}
  catch(_){list.replaceChildren(node('li','事件记录暂时无法读取；任务状态仍以当前查询为准。','muted'));}
}
function renderFigures(value) {
  const host = $('#figures'), summary = $('#figures-summary');
  host.replaceChildren();
  const artifacts = (value.artifacts || []).filter(a => {
    const t = String(a.artifact_type || '').toLowerCase(), p = String(a.path || a.relative_path || '').toLowerCase();
    return t.includes('figure') || t.includes('fig') || /\.(png|jpe?g|svg|tiff?)$/.test(p);
  });
  const workspacePlans=(value.figure_reference_workspace?.plans||[]).flatMap(item=>
    Array.isArray(item?.plan?.references) ? item.plan.references.map(reference=>({
      ...reference, reference_plan_artifact_id:item.artifact_id,
      revision_id:item.revision_id, historical:item.revision_id && String(item.revision_id)!==String(value.legacy_runner?.revision),
    })) : []);
  const refs = Array.isArray(value.figure_references) ? value.figure_references : (Array.isArray(value.figure_comparison?.references) ? value.figure_comparison.references : workspacePlans);
  const current = Array.isArray(value.figure_comparison?.current) ? value.figure_comparison.current : [];
  const bridgeCandidates=(value.skill_bridge?.figure_candidates||[]).map(item=>({
    ...item, previewable:true,
    content_url:`${taskUrl}/figure-files/${encodeURIComponent(item.relative_path||item.filename)}`,
  }));
  const rows = artifacts.length ? [...artifacts, ...bridgeCandidates] : [...bridgeCandidates, ...refs, ...current];
  if (!rows.length) { summary.textContent = '当前任务没有可核对的图件记录。图件预览与参考/当前差异比较尚不可用。'; host.appendChild(node('div','暂无图件数据，系统不会把普通论文文件冒充图件。','figure-unavailable')); return; }
  summary.textContent = `已找到 ${rows.length} 项图件记录；仅显示任务中实际登记的文件和可追溯差异。`;
  const byId = new Map(current.map(x => [x.figure_id || x.artifact_id, x]));
  for (const item of rows) {
    const row = node('div','', 'figure-row');
    const name = item.filename || item.figure_id || item.name || item.artifact_type || '图件';
    row.appendChild(node('strong', name, 'figure-meta'));
    const src = item.previewable ? item.content_url : (item.content_url || null);
    const media = String(item.media_type || item.mime_type || item.preview_media_type || '').toLowerCase();
    if (src && media==='application/pdf') { const frame = document.createElement('iframe'); frame.src = src; frame.title = `${name} PDF 预览`; frame.loading = 'lazy'; row.appendChild(frame); }
    else if (src && (media.startsWith('image/') || /\.(png|jpe?g|svg)(\?|$)/i.test(String(item.path || item.name || src)))) { const img = document.createElement('img'); img.src = src; img.alt = name; img.loading = 'lazy'; row.appendChild(img); }
    else row.appendChild(node('div','当前图件预览不可用，仅可下载或查看登记信息。','figure-unavailable'));
    if (item.historical || item.freshness === 'stale') row.appendChild(node('div','历史版本：仅用于比较，不能作为当前审核通过依据。','muted'));
    if(item.download_url){const download=node('a','下载此图件');download.href=item.download_url;row.appendChild(download);}
    const compare = byId.get(item.figure_id || item.artifact_id) || item;
    const diff = compare.differences || compare.retained_differences || compare.diff_summary;
    row.appendChild(node('div', diff ? `差异：${Array.isArray(diff) ? diff.join('；') : diff}` : '参考/当前版本差异：尚无可核对记录。','figure-meta'));
    host.appendChild(row);
  }
}
async function renderDeliveryManifest(value) {
  const summary=$('#delivery-summary'), issues=$('#delivery-issues');
  if(!id || !summary || !issues) return;
  try {
    const manifest=value.delivery_manifest || await jsonRequest(`${taskUrl}/delivery/manifest`);
    if(manifest.error) throw new Error(manifest.error.message||'交付清单暂不可用');
    summary.textContent=manifest.ready ? '当前任务已满足本地交付清单条件；投稿仍需单独确认。' : `尚未达到本地交付就绪条件（当前版本 ${manifest.task_version}）。`;
    issues.replaceChildren();
    for(const blocker of manifest.blockers||[])issues.appendChild(node('li',blocker));
    const openFindings = manifest.open_blocking_findings ?? (manifest.open_blocking_finding_ids || []).map(finding_id => ({finding_id}));
    for (const finding of openFindings) {
      const label = finding.review_id ? `${finding.review_id} / ${finding.finding_id}` : finding.finding_id;
      issues.appendChild(node('li', `存在未关闭的阻塞审核问题：${label}`));
    }
    if(manifest.package_artifact_id) issues.appendChild(node('li',`当前交付包：${manifest.package_artifact_id}`));
    if(!manifest.ready && !openFindings.length && !manifest.package_artifact_id) issues.appendChild(node('li','尚未登记新鲜的本地交付包。'));
  } catch (_) { summary.textContent='交付清单暂时无法读取；任务文件不会因此丢失。'; }
}
function renderWorkflowFiles(value) {
  const card=$('#workflow-files-card'), host=$('#workflow-files'), summary=$('#workflow-files-summary');
  if(!card||!host)return;
  const bridge=value.skill_bridge||{}; const files=Array.isArray(bridge.files)?bridge.files:[];
  host.replaceChildren();
  const ready=Boolean(value.delivery_manifest?.ready);
  const feedbackFile=$('#feedback-file'), feedbackSubmit=$('#feedback-upload-form button[type="submit"]');
  if(feedbackFile)feedbackFile.disabled=!ready;
  if(feedbackSubmit)feedbackSubmit.disabled=!ready;
  if(!ready)$('#feedback-upload-status').textContent='完成当前论文包并通过交付检查后，这里才接受用户/审稿人意见。';
  if(!files.length){summary.textContent='工作流文件尚未生成；完成一次材料、配置或任务推进后会自动出现。';return;}
  const phase=bridge.current_decision_phase==='figure'?'当前等待图件选择':bridge.current_decision_phase==='motivation'?'当前等待动机/贡献选择':'';
  summary.textContent=`当前阶段：${stageNames[bridge.stage]||bridge.stage||'处理中'}。${phase}。这些文件可供宿主 Agent 读取，也可由你下载查看。`;
  for(const file of files){const row=node('div','', 'workflow-file');const link=node('a',file.name);link.href=`${taskUrl}/skill-files/${encodeURIComponent(file.name)}`;link.target='_blank';link.rel='noopener';row.appendChild(link);if(file.size_bytes!==undefined)row.appendChild(node('span',` · ${formatSize(file.size_bytes)}`,'muted'));host.appendChild(row);}
}
function showRecovery(value) {
  const recovery = value.recovery, card = $('#recovery-card'), b = $('#continue-work');
  card.hidden = !recovery; if (!recovery) return;
  $('#recovery-message').textContent = recovery.message;
  b.textContent = recovery.retryable ? '安全重试' : '我已核对，确认未执行后继续';
  if (inFlight.has('recovery')) return;
  b.disabled = false;
  b.onclick = async () => {
    if (inFlight.has('recovery')) return;
    inFlight.add('recovery'); b.disabled = true;
    try {
      const fresh = await refreshTask(); if (!fresh?.recovery) return;
      const current = fresh.recovery;
      // The user's clicked action must still refer to the same recovery boundary.
      if (current.operation_id !== recovery.operation_id || current.retryable !== recovery.retryable) {
        notice('需要继续的工作已变化，请核对当前提示。'); return;
      }
      const result = await jsonRequest(`${taskUrl}/recovery`,{operation_id:current.operation_id,expected_version:fresh.task_version,confirm_no_effect:!current.retryable});
      if (result.error) { notice(result.error.message); return; }
      for (const [key,saved] of pending) if (saved.body.command_id === current.operation_id) {
        clearPending(key); if (key === 'configuration') dirtyConfig.clear();
      }
      clearNotice(); render(result.projection);
    } catch (_) { notice('继续请求的结果尚未核对，请先重新连接同一任务。'); }
    finally { inFlight.delete('recovery'); b.disabled=false; await refreshTask(); }
  };
}
function showDecisions(value) {
  const decisions = $('#decisions');
  const selected = new Map([...decisions.querySelectorAll('[data-decision-id]')].map(row=>[row.dataset.decisionId,row.querySelector('select')?.value]));
  decisions.replaceChildren();
  for (const d of value.decisions || []) {
    const decisionType=String(d.decision_type||'').toLowerCase();
    const phase=decisionType.includes('figure')||decisionType.includes('visual')||decisionType.includes('plot')||decisionType.includes('chart')
      ? '图件选择' : decisionType.includes('motivation')||decisionType.includes('contribution')||decisionType.includes('hypothesis')||decisionType.includes('research_question')
        ? '动机与贡献选择' : '用户选择';
    const row=node('div',`${phase} · ${d.status==='resolved'?'已确认':'待确认'}：${d.prompt||d.decision_type}`,'decision');
    row.dataset.decisionId=d.decision_id; row.dataset.decisionStatus=d.status;
    const candidates=d.candidate_preparation?.candidates||d.candidates;
    if(Array.isArray(candidates)&&candidates.length){const list=document.createElement('ul');list.className='decision-candidates';for(const candidate of candidates){const item=document.createElement('li');item.textContent=`${candidate.candidate_id||candidate.id||'候选项'}：${candidate.statement||candidate.label||''}`;list.appendChild(item);}row.appendChild(list);}
    if (d.stale) row.appendChild(node('span','（输入变化，需重新核对）','muted'));
    if (d.status==='pending') {
      const select=document.createElement('select');select.setAttribute('aria-label',d.prompt||d.decision_type);
      for (const option of d.allowed_decision_details || (d.allowed_decisions||[]).map(x=>({option_id:x,label:x}))) {
        const o=node('option',option.label);o.value=option.option_id;select.appendChild(o);
      }
      if ([...select.options].some(o=>o.value===selected.get(d.decision_id))) select.value=selected.get(d.decision_id);
      const key='decision-'+d.decision_id, b=node('button',pending.has(key)?'核对并重试原选择':'确认选择');
      select.disabled=pending.has(key);b.disabled=inFlight.has(key);
      b.onclick=async()=>{
        if (pending.has(key)) {await retry(key);return;}
        const option=select.value; b.disabled=true;
        const fresh=await refreshTask(); if (!fresh) {b.disabled=false;return;}
        await mutation(key,`${taskUrl}/decisions/${encodeURIComponent(d.decision_id)}/resolution`,{
          command_id:'resolve-'+crypto.randomUUID(),expected_version:fresh.task_version,
          payload:{decision_id:d.decision_id,option_id:option,confirmed_at:new Date().toISOString(),reason:'Confirmed in Product Web'}});
        renderedVersion=null; if(latest) render(latest);
      };
      row.append(' ',select,' ',b);
    }
    decisions.appendChild(row);
  }
  if (!(value.decisions||[]).length) decisions.appendChild(node('p','暂无待确认选择。','muted'));
}
function renderInventory(value) {
  const inventory=value.material_inventory, grants=value.material_grants||[];
  const grantView=$('#material-grants');grantView.replaceChildren();
  for(const grant of grants) grantView.appendChild(node('p',`${grant.uri} · 本任务只读授权`));
  const table=$('#material-files'),tbody=table.querySelector('tbody');tbody.replaceChildren();
  const entries=inventory?.entries;
  table.hidden=!Array.isArray(entries)||entries.length===0;
  const issues=$('#inventory-issues');issues.replaceChildren();
  if (!Array.isArray(entries)) {
    $('#inventory-summary').textContent='尚无已核对的文件清单。请授权材料文件夹并完成盘点；仅有授权编号不代表已读取文件。';return;
  }
  $('#inventory-summary').textContent=`已盘点 ${entries.length} 个文件，共 ${formatSize(inventory.total_size_bytes)}。${inventory.scan_issues?.length?'部分材料需处理下方提示。':''}`;
  for(const file of entries) {
    const grant=grants.find(g=>g.runner_grant_id===file.grant_id||g.grant_id===file.grant_id);
    const source=(inventory.grants||[]).find(g=>g.grant_id===file.grant_id);
    const row=document.createElement('tr');
    const authorized=Boolean(grant?.scope==='read_only'||source?.read_only);
    for(const text of [file.relative_path,formatSize(file.size_bytes),authorized?'已授权本机只读':'授权状态待核对','已盘点']) row.appendChild(node('td',text));
    tbody.appendChild(row);
  }
  for(const issue of inventory.scan_issues||[]) issues.appendChild(node('li',issue.message||'有文件未能完成读取，请核对材料权限。'));
}
function formatSize(size) {if(!Number.isFinite(size))return '大小未提供';return size>=1024*1024?`${(size/1024/1024).toFixed(1)} MiB`:size>=1024?`${(size/1024).toFixed(1)} KiB`:`${size} 字节`;}
function renderConfiguration(value) {
  const config=value.configuration || configDefaults;
  for(const [key,selector] of Object.entries(configFields)) {
    if(dirtyConfig.has(key)||pending.has('configuration')) continue;
    if(key==='target') {$('#target-status').value=config.target?.status||'unknown';$('#target-name').value=config.target?.name||'';}
    else if(key==='formats') {
      const formats=config.formats || (config.deliverables||[]).map(x=>({word:'docx',latex:'tex'}[x]||x));
      for(const [suffix,format] of [['pdf','pdf'],['word','docx'],['latex','tex']]) $(`#deliverable-${suffix}`).checked=formats.includes(format);
    } else if(key==='network_policy') $('#allow-network').checked=Boolean(config.network_policy?.allow_network);
    else if(key==='privacy') $('#allow-external-processing').checked=Boolean(config.privacy?.allow_external_processing);
    else if(key==='author_voice_restoration') $('#author-voice-restoration').value=config.author_voice_restoration || 'off';
    else if(key==='budget') {$('#budget-time').value=config.budget?.time_minutes ?? '';$('#budget-token').value=config.budget?.token_limit ?? '';$('#budget-cost').value=config.budget?.cost_limit ?? '';}
    else $(selector).value=config[key] ?? configDefaults[key];
  }
  if(!pending.has('configuration')) updateTarget();
  const list=$('#preserved-settings');list.replaceChildren();
  const saved=value.configuration;
  const labels={off:'暂不启用',standard:'标准',strict:'严格'};
  const budget=saved?.budget;
  const items=[['公开联网检索',saved?(saved.network_policy?.allow_network?'已允许':'未允许'):'首次保存默认不允许'],
    ['外部处理材料',saved?(saved.privacy?.allow_external_processing?'已有许可保持原值':'未允许'):'首次保存默认不允许'],
    ['外部上传','禁用'],['作者表达',saved?labels[saved.author_voice_restoration]||'按已有设置':'暂不启用'],
    ['预算',budget?`时间 ${budget.time_minutes??'未设置'} 分钟；Token ${budget.token_limit??'未设置'}；成本 ${budget.cost_limit??'未设置'}`:'尚未设置'],
    ['协作',saved?.interaction?.mode==='delegated_local_test'?'保留历史配置；当前业务选择仍由用户确认':'用户逐项确认']];
  for(const [label,text] of items) list.append(node('dt',label),node('dd',text));
  if (!configLoaded) {
    $('#config-message').textContent=value.configuration_source==='agent_proposal'
      ? 'AI 根据当前对话预填了设置，尚未保存；请核对、修改后点击“保存设置”。保存前不会开始论文工作。'
      : value.configuration_source==='legacy_runner'
      ? '已读取旧工作台设置。请核对后保存一次，迁移到新双接口。'
      : saved ? '已读取保存的设置。' : '尚未保存任务设置.';
    configLoaded=true;
  }
}
for(const [key,selector] of Object.entries(configFields)) {
  const selectors=key==='target'?['#target-status','#target-name']:key==='formats'?['#deliverable-pdf','#deliverable-word','#deliverable-latex']:key==='budget'?['#budget-time','#budget-token','#budget-cost']:[selector];
  for(const s of selectors) $(s).addEventListener('input',()=>{dirtyConfig.add(key);if(key==='target') updateTarget();});
}
$('#config-form').onsubmit=async event=>{
  event.preventDefault(); if(pending.has('configuration')) {notice('请先核对原设置请求的结果。',$('#config-message'));return;}
  const targetStatus=$('#target-status').value,targetName=$('#target-name').value.trim();
  const formats=[['pdf','pdf'],['word','docx'],['latex','tex']].filter(([suffix])=>$(`#deliverable-${suffix}`).checked).map(([,format])=>format);
  if(!formats.length) {notice('至少选择一种本地交付物。',$('#config-message'));return;}
  if(targetStatus==='known'&&!targetName) {notice('目标状态为已确定时必须填写名称。',$('#config-message'));return;}
  const optionalNumber=selector=>{const raw=$(selector).value.trim();return raw===''?null:Number(raw);};
  const values={workflow:$('#workflow').value,scene:$('#scene').value,requested_scope:$('#requested-scope').value,
    target:{status:targetStatus,name:targetStatus==='known'?targetName:null},output_language:$('#output-language').value,formats,
    network_policy:{allow_network:$('#allow-network').checked,allow_external_upload:false},
    privacy:{allow_external_processing:$('#allow-external-processing').checked},
    author_voice_restoration:$('#author-voice-restoration').value,
    budget:{time_minutes:optionalNumber('#budget-time'),token_limit:optionalNumber('#budget-token'),cost_limit:optionalNumber('#budget-cost')}};
  const changed=new Set(dirtyConfig);
  const fresh=await refreshTask();if(!fresh) return;
  let patch;
  if(fresh.configuration) patch=Object.fromEntries([...changed].map(key=>[key,values[key]]));
  else patch={...values};
  if(!Object.keys(patch).length) {notice('设置未变化。',$('#config-message'),false);return;}
  const endpoint=$('#config-form').dataset.endpoint.replace('{task_id}',encodeURIComponent(id));
  await mutation('configuration',endpoint,{schema_version:'1.1',command_id:'web-config-'+crypto.randomUUID(),expected_version:fresh.task_version,payload:patch});
};
$('#retry-configuration').onclick=()=>retry('configuration');
$('#materials-form').onsubmit=async event=>{
  event.preventDefault();notice('材料授权由宿主 Agent 完成；网页只显示当前任务材料清单。',$('#material-message'));return;
  /* if(pending.has('materials')) {notice('请先核对原材料请求的结果。',$('#material-message'));return;}
  const uri=$('#material-path').value.trim();if(!uri||!$('#material-consent').checked) return;
  const fresh=await refreshTask();if(!fresh) return;
  await mutation('materials',`${taskUrl}/materials`,{schema_version:'1.1',command_id:'web-materials-'+crypto.randomUUID(),expected_version:fresh.task_version,
    payload:{grants:[{grant_id:'materials-'+crypto.randomUUID(),uri,scope:'read_only'}]}}); */
};
$('#retry-materials').onclick=()=>retry('materials');
$('#additional-materials-form').onsubmit=async event=>{
  event.preventDefault();notice('补充材料由宿主 Agent 登记；网页只显示结果。',$('#additional-material-message'));return;
  /*
  if(pending.has('additional-materials')) {notice('请先核对原补充材料请求的结果。',$('#additional-material-message'));return;}
  const uri=$('#additional-material-path').value.trim();
  if(!uri||!$('#additional-material-consent').checked) {notice('请填写补充材料路径并确认本机只读授权。',$('#additional-material-message'));return;}
  const fresh=await refreshTask();if(!fresh)return;
  await mutation('additional-materials',`${taskUrl}/materials`,{schema_version:'1.1',command_id:'web-additional-materials-'+crypto.randomUUID(),expected_version:fresh.task_version,
    payload:{grants:[{grant_id:'materials-'+crypto.randomUUID(),uri,scope:'read_only'}]}}); */
};
$('#retry-additional-materials').onclick=()=>retry('additional-materials');
function filterMaterials(){const search=$('#material-filter').value.trim().toLocaleLowerCase();for(const row of $('#material-files tbody').rows)row.hidden=!row.textContent.toLocaleLowerCase().includes(search);}
$('#material-filter').oninput=filterMaterials;
$('#revision-request-form').onsubmit=async event=>{
  event.preventDefault(); const feedback=$('#revision-request-feedback').value.trim(), scope=$('#revision-request-scope').value;
  if(!feedback){$('#revision-request-status').textContent='请填写修改意见。';return;}
  const fresh=await refreshTask(); if(!fresh)return;
  $('#revision-request-submit').disabled=true; $('#revision-request-status').textContent='正在登记…';
  try {const result=await jsonRequest(`${taskUrl}/runner/revision-request`,{schema_version:'1.1',command_id:'web-revision-'+crypto.randomUUID(),expected_version:fresh.task_version,expected_revision:fresh.legacy_runner?.revision,payload:{feedback,scope}});
    if(result.error) $('#revision-request-status').textContent=result.error.message||'修改意见未登记，请核对后重试。';
    else {$('#revision-request-feedback').value='';$('#revision-request-status').textContent='修改意见已登记，将在同一任务中继续修回。'; await refreshTask();}
  }catch(_){$('#revision-request-status').textContent='连接中断，尚未确认修改意见是否已登记。请刷新同一任务核对，不要重复提交。';}
  finally{$('#revision-request-submit').disabled=latest?.legacy_runner?.stage!=='target_package_ready';}
};
$('#runner-bootstrap').onclick=()=>notice('流程启动由宿主 Agent 完成。');
$('#runner-resume').onclick=()=>notice('阶段推进由宿主 Agent 完成。');
$('#create-form')?.addEventListener('submit', async event=>{
  event.preventDefault();notice('网页端不创建任务；请由宿主 Agent 创建并打开同一任务链接。');
});
$('#resume-form')?.addEventListener('submit', event=>{event.preventDefault();notice('任务恢复由宿主 Agent 完成；请打开宿主提供的同一任务链接。');});
$('#refresh-task').onclick=refreshTask;
$('#copy-handoff').onclick=async()=>{try{await navigator.clipboard.writeText($('#host-handoff').value);$('#handoff-status').textContent='已复制，请粘贴到原 Agent 对话中继续；网页没有自动启动 AI。';}catch(_){$('#host-handoff').focus();$('#host-handoff').select();$('#handoff-status').textContent='浏览器未允许自动复制。指引已选中，请按 Ctrl+C 复制。';}};
$('#open-package').onclick=async()=>{const status=$('#open-package-status');status.textContent='正在打开本地工作包目录…';try{const result=await jsonRequest(`${taskUrl}/open-package`,{});if(result.error)throw Error(result.error.message);status.textContent=result.opened?`已打开：${result.package_directory}`:`工作包目录：${result.package_directory}（请在文件管理器中打开）`;}catch(error){status.textContent=error.message||'目录尚未可用，请刷新任务。';}};
$('#copy-figure-handoff').onclick=async()=>{const status=$('#figure-handoff-status');const names=[...(latest?.skill_bridge?.files||[])].filter(file=>file.name==='04_figure_choice.json').map(file=>file.name);const text=`请继续同一 PaperSpine 任务 ${latest?.task_id||id} 的图件选择。先读取 workflow/04_figure_choice.json，检查当前候选文件与参考图；统一配色、字体、网格、面板和标注后再重生成可编辑图件，并重新渲染和独立复审。网页当前显示的候选文件：${names.join(', ')||'尚未生成'}。`;try{await navigator.clipboard.writeText(text);status.textContent='图件续作指引已复制，请粘贴到宿主 Agent 对话。';}catch(_){status.textContent=text;}};
$('#feedback-upload-form').onsubmit=async event=>{event.preventDefault();const status=$('#feedback-upload-status'), file=$('#feedback-file').files[0];if(!file){status.textContent='请选择 .md 或 .txt 意见文件。';return;}if(file.size>32000){status.textContent='意见文件不能超过 32 KB。';return;}status.textContent='正在写入同一任务并登记修回…';try{const content=await file.text();const fresh=await refreshTask();if(!fresh)throw Error('无法读取当前任务');const result=await jsonRequest(`${taskUrl}/feedback`,{filename:file.name,feedback:content,scope:'user_uploaded_feedback'});if(result.error)throw Error(result.error.message);status.textContent='意见已写入同一任务；宿主 Agent 可读取 workflow/05_review_feedback.json 继续修回。';await refreshTask();}catch(error){status.textContent=error.message||'意见写入结果尚未确认，请刷新同一任务。';}};
async function loadRecentTasks(){const container=$('#recent-tasks');try{const value=await jsonRequest('/api/v1/tasks');if(value.error)throw Error();container.replaceChildren();for(const task of value.tasks||[]){const row=node('p',''),link=node('a',task.title||task.task_id);link.href='/?task_id='+encodeURIComponent(task.task_id);row.append(link,node('br'),node('span',task.description||'任务简介暂不可用','muted'),node('small',` · ${task.task_id}`,'muted'));container.appendChild(row);}if(!container.children.length)container.textContent='暂无可查看的论文任务，请由宿主 Agent 打开任务链接。';}catch(_){container.textContent='最近任务暂不可读；请由宿主 Agent 提供同一任务链接。';}}
if (!id) {$('#welcome').hidden=false;$('#status').textContent='等待宿主 Agent 打开任务';loadRecentTasks();}
else {
  refreshTask();setInterval(()=>{if(!document.hidden) refreshTask();},3000);
  const stream=new EventSource(`${taskUrl}/events`);
  stream.addEventListener('task-event',event=>{const value=JSON.parse(event.data);const row=node('li',value.event_type);row.dataset.eventId=value.event_id;$('#events').appendChild(row);});
  stream.addEventListener('snapshot-end',()=>stream.close());
}
