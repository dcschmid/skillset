-- Fixture: unknown-to-the-generic-tables language (Lua).
-- Generic audit mode must report metrics without claiming semantic analysis.
local function spawn(pos, hp)
  local e = { x = pos.x, y = pos.y, hp = hp }
  if hp > 100 then
    e.elite = true
  end
  return e
end
return { spawn = spawn }
