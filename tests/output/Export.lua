local lfs = require('lfs')
local success, error = pcall(function()
    log.write(%log_prefix%, log.INFO, "Loading script: PyDcsExport.lua")
    dofile(lfs.writedir()..[[Scripts\PyDcsExport.lua]])
end)

if not success then
    log.write(%log_prefix%, log.ERROR, "Failed to load script PyDcsExport.lua: " .. tostring(error))
end
