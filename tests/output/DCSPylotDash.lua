--[[

]]

-- internal functions

local function to_deg_min_sec(deg_dec)
   local deg = math.floor(deg_dec)
   local min_dec = (deg_dec - deg) * 60
   local min = math.floor(min_dec)
   local sec_dec = (min_dec - min) * 60
   return deg, min_dec, min, sec_dec
end

local function to_dcml_str(nesw, deg, min_dec)
    return nesw .. " " .. string.format("%02d",deg) .. "°" .. string.format("%06.3f'", min_dec)
end

local function to_sec_str(nesw, deg, min, sec_dec, precise)
    local sec_str = precise and string.format("%05.2f\"", sec_dec) or string.format("%02d", math.floor(sec_dec + 0.5)) .. "\""
    return nesw .. " " .. string.format("%02d",deg) .. "°" .. string.format("%02d",min) .. "'" .. sec_str
end


-- public functions for single values

local function to_lat_dcml_str(lat_dec)
    local lat_deg, lat_min_dec, _, _ = to_deg_min_sec(lat_dec)
    local ns = lat_deg > 0 and "N" or "S"
    return to_dcml_str(ns, lat_deg, lat_min_dec)
end

local function to_lon_dcml_str(lon_dec)
    local lon_deg, lon_min_dec, _, _ = to_deg_min_sec(lon_dec)
    local ew = lon_deg > 0 and "E" or "W"
    return to_dcml_str(ew, lon_deg, lon_min_dec)
end

local function to_lat_sec_str(lat_dec, precise)
    local lat_deg, _, lat_min, lat_sec_dec = to_deg_min_sec(lat_dec)
    local ns = lat_deg > 0 and "N" or "S"
    return to_sec_str(ns, lat_deg, lat_min, lat_sec_dec, precise)
end

local function to_lon_sec_str(lon_dec, precise)
    local lon_deg, _, lon_min, lon_sec_dec = to_deg_min_sec(lon_dec)
    local ew = lon_deg > 0 and "E" or "W"
    return to_sec_str(ew, lon_deg, lon_min, lon_sec_dec, precise)
end

local to_lat_sec_precise_str = function(lat_dec)
    return to_lat_sec_str(lat_dec, true)
end
local to_lon_sec_precise_str = function(lon_dec)
    return to_lon_sec_str(lon_dec, true)
end

-- public functions for pair values

local function to_lat_lon_dcml_str(lat_dec, lon_dec)
    return to_lat_dcml_str(lat_dec) .. "   " .. to_lon_dcml_str(lon_dec)
end

local function to_lat_lon_sec_str(lat_dec, lon_dec, precise)
    local lat_function = precise and to_lat_sec_precise_str or to_lat_sec_str
    local lon_function = precise and to_lon_sec_precise_str or to_lon_sec_str
    return lat_function(lat_dec) .. "   " .. lon_function(lon_dec)
end


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
                    "Access-Control-Allow-Origin: *\r\n" ..
                    "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" ..
                    "Access-Control-Allow-Headers: Content-Type\r\n" ..
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
    data.ias.kts = airspeed * 1.9438400000000633
    data.mach = mach
    data.tas = {}
    data.tas.kts = tas * 1.9438400000000633
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
end
