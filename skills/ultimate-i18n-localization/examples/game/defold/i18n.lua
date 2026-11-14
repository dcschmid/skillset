-- i18n.lua — portable Defold localization module (fixture/pattern).
-- Engine-free core: pure Lua, testable under luajit/luatricks without Defold.
-- In Defold, wire load() to sys.load_resource + json.decode (see NOTES.md).
local i18n = { locale = "en", fallback = "en", tables = {}, fonts = {}, rtl = { ar = true, he = true } }

local function decode_json(text)
  -- minimal flat JSON string-map decoder (Lua patterns, NOT regex):
  -- {"key":"value","k2":"v2"}; handles \" and \n inside values is limited —
  -- for nested JSON use a full library (e.g. json4lua) inside Defold.
  local out = {}
  for k, v in text:gmatch('"([%w_%./%-]+)"%s*:%s*"([^"]*)"') do
    out[k] = (v:gsub('\\n', '\n'):gsub('\\"', '"'))
  end
  return out
end
i18n.decode_json = decode_json

function i18n.register(locale, tbl) i18n.tables[locale] = tbl return i18n end
function i18n.load(locale, raw_text) return i18n.register(locale, decode_json(raw_text)) end

function i18n.is_rtl(locale) return i18n.rtl[(locale or i18n.locale):match'^%l+' or ''] == true end

function i18n.t(key, params)
  local tbl = i18n.tables[i18n.locale] or i18n.tables[i18n.fallback] or {}
  local s = tbl[key] or (i18n.tables[i18n.fallback] or {})[key] or key
  if params then
    s = (s:gsub('{(%w+)}', function(p) return params[p] ~= nil and tostring(params[p]) or ('{%s}'):format(p) end))
  end
  return s
end

-- GUI layout direction for a language: pivot swap, NOT blanket mirroring.
function i18n.pivot(locale) return i18n.is_rtl(locale) and 'TEXT_PIVOT_E' or 'TEXT_PIVOT_W' end

function i18n.set_locale(locale)
  if not i18n.tables[locale] and locale ~= i18n.fallback then return false end
  i18n.locale = locale
  return true, i18n.is_rtl(locale)
end
return i18n
