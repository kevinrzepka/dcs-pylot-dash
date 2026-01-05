local lfs = require('lfs')
local success, error = pcall(function()
    log.write("DCSPylotDash", log.INFO, "Loading script: DCSPylotDash.lua")
    dofile(lfs.writedir()..[[Scripts\DCSPylotDash.lua]])
end)

if not success then
    log.write("DCSPylotDash", log.ERROR, "Failed to load script DCSPylotDash.lua: " .. tostring(error))
end
