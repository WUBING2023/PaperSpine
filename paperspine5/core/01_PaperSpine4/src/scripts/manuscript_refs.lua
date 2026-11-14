-- Semantic figure/table references before citeproc; native fields at export.
-- Run once to JSON, then on that JSON for docx/latex. No citation styling here.
local targets, counts, number_labels = {}, {Figure = 0, Table = 0}, {}
local titles = {Figure = 'Figure', Table = 'Table'}
local function fail(message) error('manuscript references: ' .. message, 0) end
local function xml(value)
  return tostring(value):gsub('&', '&amp;'):gsub('<', '&lt;'):gsub('>', '&gt;'):gsub('"', '&quot;')
end
local function register(el, kind, prefix)
  local id = el.identifier
  if id == '' then fail(kind .. ' caption needs an ID (#' .. prefix .. ':name)') end
  if not id:match('^' .. prefix .. ':[%w_.%-]+$') and not (kind == 'Table' and id:match('^tab:[%w_.%-]+$')) then fail(kind .. ' has invalid or wrong-kind ID: ' .. id) end
  if targets[id] then fail('duplicate ID: ' .. id) end
  -- Markdown implicit figures put classes/custom attributes on their Image.
  local image
  if el.t == 'Figure' and #el.content == 1 and el.content[1].content and #el.content[1].content == 1 then
    if el.content[1].content[1].t == 'Image' then image = el.content[1].content[1] end
  end
  local unnumbered = el.classes:includes('unnumbered') or (image and image.classes:includes('unnumbered'))
  if not unnumbered then counts[kind] = counts[kind] + 1 end
  targets[id] = {kind = kind, title = titles[kind], number = number_labels[id] or counts[kind], explicit_number = number_labels[id] ~= nil, unnumbered = unnumbered,
    label = el.attributes['ref-label'] or (image and image.attributes['ref-label']), bookmark = 'ps_' .. prefix .. '_' .. pandoc.utils.sha1(id):sub(1, 24)}
end
local function target(id)
  if not targets[id] then fail('missing figure/table destination: ' .. id) end
  return targets[id]
end
local function field(instruction, value, anchor)
  local result = '<w:r><w:t>' .. xml(value) .. '</w:t></w:r>'
  if anchor then result = '<w:hyperlink w:anchor="' .. xml(anchor) .. '">' .. result .. '</w:hyperlink>' end
  return '<w:fldSimple w:instr="' .. xml(instruction) .. '">' .. result .. '</w:fldSimple>'
end
local function reference(span)
  if not span.classes:includes('ps-xref') then return nil end
  local id = span.attributes.target
  local t = target(id)
  local label = t.unnumbered and t.label or (t.title .. ' ' .. t.number)
  if not label then fail('unnumbered reference requires ref-label: ' .. id) end
  if FORMAT == 'docx' then
    if t.unnumbered then
      return pandoc.RawInline('openxml', '<w:hyperlink w:anchor="' .. t.bookmark .. '"><w:r><w:t>' .. xml(label) .. '</w:t></w:r></w:hyperlink>')
    end
    local number = pandoc.RawInline('openxml', field(' REF ' .. t.bookmark .. ' \\h ', t.number, t.bookmark))
    if span.attributes['number-only'] == 'true' then return number end
    return {pandoc.Str(t.title .. '\u{00a0}'), number}
  elseif FORMAT:match('latex') then
    if t.unnumbered then
      local escaped = pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(label)})}), 'latex')
      return pandoc.RawInline('latex', '\\hyperlink{' .. id .. '}{' .. escaped .. '}')
    end
    local title = pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(t.title)})}), 'latex')
    if span.attributes['number-only'] == 'true' then return pandoc.RawInline('latex', '\\ref{' .. id .. '}') end
    return pandoc.RawInline('latex', title .. '~\\ref{' .. id .. '}')
  end
end
local function citation(cite)
  local has_xref = false
  for _, item in ipairs(cite.citations) do
    if item.id:match('^fig:') or item.id:match('^tbl:') then has_xref = true end
  end
  if not has_xref then return nil end
  local result = pandoc.List()
  for i, item in ipairs(cite.citations) do
    if not (item.id:match('^fig:') or item.id:match('^tbl:')) then
      fail('put bibliography citations and figure/table references in separate groups')
    end
    local t = target(item.id)
    if t.unnumbered and not t.label then fail('unnumbered reference requires ref-label: ' .. item.id) end
    if i > 1 then result:insert(pandoc.Str(';')); result:insert(pandoc.Space()) end
    result:extend(item.prefix)
    if #item.prefix > 0 then result:insert(pandoc.Space()) end
    result:insert(pandoc.Span({pandoc.Str(t.unnumbered and t.label or (t.title .. ' ' .. t.number))},
      pandoc.Attr('', {'ps-xref'}, {target = item.id})))
    result:extend(item.suffix)
  end
  return result
end
local bookmark_id = 1000000
local function caption(el)
  local t = target(el.identifier)
  if FORMAT:match('latex') and t.explicit_number then
    local command = t.kind == 'Figure' and 'thefigure' or 'thetable'
    local label = pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(tostring(t.number))})}), 'latex')
    return {pandoc.RawBlock('latex', '\\begingroup\\renewcommand{\\' .. command .. '}{' .. label .. '}'),
            el, pandoc.RawBlock('latex', '\\endgroup')}
  end
  if FORMAT == 'docx' then
    bookmark_id = bookmark_id + 1
    local start = '<w:bookmarkStart w:id="' .. bookmark_id .. '" w:name="' .. t.bookmark .. '"/>'
    local finish = '<w:bookmarkEnd w:id="' .. bookmark_id .. '"/>'
    local prefix = pandoc.List()
    if t.unnumbered then
      if el.t ~= 'Figure' then prefix:insert(pandoc.RawInline('openxml', start .. finish)) end
    else
      prefix:insert(pandoc.Str(t.title .. ' '))
      local numbered = t.explicit_number and ('<w:r><w:t>' .. xml(t.number) .. '</w:t></w:r>') or field(' SEQ ' .. t.kind .. ' \\* ARABIC ', t.number)
      prefix:insert(pandoc.RawInline('openxml', start .. numbered .. finish))
      prefix:insert(pandoc.Str('. '))
    end
    if #el.caption.long == 0 then fail('empty caption: ' .. el.identifier) end
    local first = el.caption.long[1]
    if first.t ~= 'Plain' and first.t ~= 'Para' then fail('caption must start with text: ' .. el.identifier) end
    prefix:extend(first.content); first.content = prefix
    el.caption.long[1] = first
    if t.unnumbered and el.t == 'Figure' then
      -- A native range bookmark starts at the whole figure, including when its
      -- caption is below. Keep the Figure ID/content intact for venue filters;
      -- inserting raw anchors into its content changes Pandoc's image layout.
      return pandoc.Div({el}, pandoc.Attr(t.bookmark))
    end
    return el
  elseif FORMAT:match('latex') and t.unnumbered then
    if el.t ~= 'Figure' then fail('unnumbered tables are not supported by the LaTeX exporter') end
    -- Keep the destination inside the float, before its visual content. End
    -- the anchor paragraph so an image cannot move it down to its baseline.
    local blocks = pandoc.List({pandoc.RawBlock('latex', '\\begin{figure}\n\\centering\n\\hypertarget{' .. el.identifier .. '}{}\\par')})
    blocks:extend(el.content)
    local caption_text = pandoc.write(pandoc.Pandoc(el.caption.long), 'latex')
    blocks:insert(pandoc.RawBlock('latex', '\\caption*{' .. caption_text .. '}\n\\end{figure}'))
    return blocks
  end
end
function Pandoc(doc)
  local needs_float = false
  -- Pandoc's LaTeX reader before 3.12 stores a table's \label on a
  -- single-table Div. Move only that native object label to the Table so
  -- registration, Word fields and LaTeX captions share one destination.
  doc = doc:walk({Div = function(el)
    if #el.content ~= 1 or el.content[1].t ~= 'Table' or el.identifier == '' then return nil end
    if not (el.identifier:match('^tbl:') or el.identifier:match('^tab:')) then return nil end
    local table = el.content[1]
    if table.identifier ~= '' and table.identifier ~= el.identifier then
      fail('conflicting table wrapper and caption IDs: ' .. el.identifier .. ' / ' .. table.identifier)
    end
    table.identifier = el.identifier
    el.identifier = ''
    el.content[1] = table
    return el
  end})
  if doc.meta['reference-labels'] then
    for id, label in pairs(doc.meta['reference-labels']) do
      number_labels[id] = pandoc.utils.stringify(label)
      if number_labels[id]:match('^%s*$') then fail('reference-labels contains an empty label: ' .. id) end
    end
  end
  for kind, key in pairs({Figure = 'figure-title', Table = 'table-title'}) do
    if doc.meta[key] then
      titles[kind] = pandoc.utils.stringify(doc.meta[key])
      if titles[kind]:match('^%s*$') then fail(key .. ' must not be empty') end
    end
  end
  doc:walk({Figure = function(el)
              if (el.attributes['latex-placement'] or ''):match('H') then needs_float = true end
              register(el, 'Figure', 'fig')
            end,
            Table = function(el) register(el, 'Table', 'tbl') end})
  if FORMAT == 'json' then
    return doc:walk({Cite = citation, Link = function(link)
      if link.attributes['reference-type'] ~= 'ref' then return nil end
      local id = link.attributes.reference
      if not targets[id] then
        if id and (id:match('^fig:') or id:match('^tbl:') or id:match('^tab:')) then target(id) end
        return nil
      end
      return pandoc.Span(link.content, pandoc.Attr('', {'ps-xref'}, {target = id, ['number-only'] = 'true'}))
    end})
  end
  doc = doc:walk({Span = reference})
  doc = doc:walk({Figure = caption, Table = caption})
  if FORMAT:match('latex') then
    local includes = doc.meta['header-includes'] or pandoc.MetaList({})
    if includes.t ~= 'MetaList' and pandoc.utils.type(includes) ~= 'List' then includes = pandoc.MetaList({includes}) end
    includes:insert(pandoc.MetaBlocks({pandoc.RawBlock('latex', '\\usepackage{caption}')}))
    if needs_float then includes:insert(pandoc.MetaBlocks({pandoc.RawBlock('latex', '\\usepackage{float}')})) end
    for kind, command in pairs({Figure = 'figurename', Table = 'tablename'}) do
      local title = pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(titles[kind])})}), 'latex')
      includes:insert(pandoc.MetaBlocks({pandoc.RawBlock('latex', '\\AtBeginDocument{\\renewcommand{\\' .. command .. '}{' .. title .. '}}')}))
    end
    doc.meta['header-includes'] = includes
  end
  return doc
end
