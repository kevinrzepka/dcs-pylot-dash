local lfs = require('lfs')
local success, error = pcall(function()
    log.write(%log_prefix%, log.INFO, "Loading script: DCSPylotDash.lua")
    dofile(lfs.writedir()..[[Scripts\DCSPylotDash.lua]])
end)

if not success then
    log.write(%log_prefix%, log.ERROR, "Failed to load script DCSPylotDash.lua: " .. tostring(error))
end
