--[[
test data

lat: 42.18190937369
lon: 42.46432455518

Metric: X-00284567 Z+00682402
Lat Long Standard: N 42°10'54"   E 42°27'51"
Lat Long Precise: N 42°10'54.87"   E 42°27'51.56"
Lat Long Decimal Minutes: N 42°10.914'   E 42°27.859'
MGRS GRID: 38 T KM 90593 73086
Altitude: 45 m / 148 feet
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
    return nesw .. " " .. deg .. "°" .. string.format("%.3f'", min_dec)
end

local function to_sec_str(nesw, deg, min, sec_dec, precise)
    local sec_str = precise and string.format("%.2f\"", sec_dec) or math.floor(sec_dec + 0.5) .. "\""
    return nesw .. " " .. deg .. "°" .. min .. "'" .. sec_str
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

local to_lat_sec_str_precise = function(lat_dec)
    return to_lat_sec_str(lat_dec, true)
end
local to_lon_sec_str_precise = function(lon_dec)
    return to_lon_sec_str(lon_dec, true)
end

-- public functions for pair values

local function to_lat_lon_dcml_str(lat_dec, lon_dec)
    return to_lat_dcml_str(lat_dec) .. "   " .. to_lon_dcml_str(lon_dec)
end

local function to_lat_lon_sec_str(lat_dec, lon_dec, precise)
    local lat_function = precise and to_lat_sec_str_precise or to_lat_sec_str
    local lon_function = precise and to_lon_sec_str_precise or to_lon_sec_str
    return lat_function(lat_dec) .. "   " .. lon_function(lon_dec)
end


-- test
local lat_dec = 42.18190937369
local lon_dec = 42.46432455518

print(to_lat_lon_dcml_str(lat_dec, lon_dec))
print(to_lat_lon_sec_str(lat_dec, lon_dec, false))
print(to_lat_lon_sec_str(lat_dec, lon_dec, true))
