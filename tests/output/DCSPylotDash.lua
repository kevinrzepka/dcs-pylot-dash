--[[

]]

local function debug_lua_environment()
    log.write("DCSPylotDash", log.INFO, log.INFO, "=== Lua Environment Debug ===")
    log.write("DCSPylotDash", log.INFO, log.INFO, "Lua version:" .. _VERSION)
    log.write("DCSPylotDash", log.INFO, log.INFO, "Package path:" .. package.path)
    log.write("DCSPylotDash", log.INFO, log.INFO, "Package cpath:" .. package.cpath)
end
debug_lua_environment()

-- Add Scripts folder in DCS installation path to lua path, otherwise modules are not found (anymore)
local dcs_scripts_path = ".\\Scripts"
package.path = package.path .. ";" .. dcs_scripts_path .. "\\?.lua"
package.path = package.path .. ";" .. dcs_scripts_path .. "\\?\\init.lua"
package.cpath = package.cpath .. ";" .. dcs_scripts_path .. "\\?.dll"
package.cpath = package.cpath .. ";" .. dcs_scripts_path .. "\\lua-?.dll"

debug_lua_environment()


local socket = require("socket")
local JSON = require("json")

-- HTTP Server Configuration
local server_host = "127.0.0.1"
local server_port = 52025

-- Global Variables
local server = nil
local clients = {}

-- Helper function to safely get data
local function safe_get(func, default)
    local success, result = pcall(func)
    if success and result ~= nil then
        return result
    else
        return default or 0
    end
end

-- Initialize HTTP Server
function LuaExportStart()
    -- Create TCP server socket
    server = socket.tcp()
    if server then
        server:setoption("reuseaddr", true)
        server:bind(server_host, server_port)
        server:listen(5)
        server:settimeout(0) -- Non-blocking
        log.write("DCSPylotDash", log.INFO, "HTTP Server started on " .. server_host .. ":" .. server_port)
    else
        log.write("DCSPylotDash", log.ERROR, "Failed to create server socket")
    end
end

-- Handle HTTP requests
local function handle_http_request(client_socket)
    local request, err = client_socket:receive()
    if not request then
        client_socket:close()
        return
    end

    -- Simple HTTP GET response
    local response_body = generate_json_data()
    local response = "HTTP/1.1 200 OK\r\n" ..
                    "Content-Type: application/json\r\n" ..
                    "Content-Length: " .. string.len(response_body) .. "\r\n" ..
                    "Connection: close\r\n\r\n" ..
                    response_body

    client_socket:send(response)
    client_socket:close()
end

-- Generate JSON data from DCS
function generate_json_data()
    local data = {}


    local airspeed = safe_get(LoGetIndicatedAirSpeed, 0)
    local mach = safe_get(LoGetMachNumber, 0)
    local tas = safe_get(LoGetTrueAirSpeed, 0)
    local heading = safe_get(LoGetMagneticYaw, 0)
    local altitude_msl = safe_get(LoGetAltitudeAboveSeaLevel, 0)
    local altitude_agl = safe_get(LoGetAltitudeAboveGroundLevel, 0)
    local engine_info = safe_get(LoGetEngineInfo, {})
    local payload_info = safe_get(LoGetPayloadInfo, {})
    data.ias = {}
    data.ias.kts = airspeed * 1.94384
    data.mach = mach
    data.tas = {}
    data.tas.kts = tas * 1.94384
    data.heading = {}
    data.heading.degrees = heading * 57.29577951308232
    data.altitude = {}
    data.altitude.msl = {}
    data.altitude.msl.ft = altitude_msl * 3.28084
    data.altitude.agl = {}
    data.altitude.agl.ft = altitude_agl * 3.28084
    data.fuel = {}
    data.fuel.internal = {}
    data.fuel.internal.lbs = engine_info.fuel_internal * 12000.0
    data.arms = {}
    data.arms.gun_rounds = payload_info.Cannon.shells

    return JSON:encode(data)
end

-- Main export function called every frame
function LuaExportAfterNextFrame()
    if not server then
        return
    end

    -- Accept new connections
    local client_socket = server:accept()
    if client_socket then
        client_socket:settimeout(0)
        handle_http_request(client_socket)
    end
end

-- Cleanup on mission end
function LuaExportStop()
    if server then
        server:close()
        server = nil
        log.write("DCSPylotDash", log.INFO, "HTTP Server stopped")
    end

    -- Close any remaining client connections
    for i, client in ipairs(clients) do
        if client then
            client:close()
        end
    end
    clients = {}
end
