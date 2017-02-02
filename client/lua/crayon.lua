local requests = require("requests")
local socket = require("socket")
local json = require('cjson.safe')

local __version__ = "0.4"

local CrayonClient = {}
local CrayonExperiment = {}

-- CrayonClient class
do
    CrayonClient.__index = CrayonClient

    local mt = {}
    mt.__call = function(cc, hostname, port)
        local self = {}
        setmetatable(self, CrayonClient)

        self.hostname = hostname or "localhost"
        self.port = port or 8889
        self.url = self.hostname .. ":" .. tostring(self.port)

        -- Add http header if missing
        function urlstartswith(pattern)
            return string.sub(self.url,1,string.len(pattern))==pattern
        end
        if not (urlstartswith("http://") or urlstartswith("https://")) then
            self.url = "http://" .. self.url
        end

        -- Check that the server is running and at the same version
        local ok, r = pcall(requests.get, self.url)
        if not ok then
            msg = "The server at "..self.hostname..":"..tostring(self.port).." does not appear to be up!"
            error(msg)
        end
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        if r.text ~= __version__ then
            local msg = "Server runs version "..r.text.." while le client runs version"..__version__.."."
            error(msg)
        end

        return self
    end
    setmetatable(CrayonClient, mt)

    function CrayonClient:get_experiment_names()
        local query = "/data"
        local r = requests.get(self.url..query)
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        return r.json()
    end

    function CrayonClient:open_experiment(xp_name)
        assert(type(xp_name)=="string")
        return CrayonExperiment(xp_name, self, false)
    end

    function CrayonClient:create_experiment(xp_name, zip_file)
        assert(type(xp_name)=="string")
        return CrayonExperiment(xp_name, self, true, zip_file)
    end

    function CrayonClient:remove_experiment(xp_name)
        assert(type(xp_name)=="string")
        query = "/data"
        local r = requests.get{
            url = self.url..query,
            params = {xp = xp_name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
    end

    function CrayonClient:remove_all_experiments()
        local xp_list = self.get_experiment_names()
        for i, xp_name in pairs(xp_list) do
            self.remove_experiment(xp_name)
        end
    end
end

-- CrayonExperiment class
do
    -- Local functions
    local __init_from_file, __init_empty, __init_from_existing
    local __update_steps, __get_name_list
    local __check_histogram_data

    local json_headers = {}
    json_headers["Content-Type"] = "application/json"
    local zip_headers = {}
    zip_headers["Content-Type"] = "application/zip"



    CrayonExperiment.__index = CrayonExperiment

    local mt = {}
    mt.__call = function(ce, xp_name, client, create, zip_file)
        local self = {}
        setmetatable(self, CrayonExperiment)

        self.client = client
        self.xp_name = xp_name
        self.scalar_steps = {}
        self.hist_steps = {}
        local mt = {__index = function() return 0 end}
        setmetatable(self.scalar_steps, mt)
        setmetatable(self.hist_steps, mt)

        if zip_file then
            if not create then
                error("Can only create a new experiment when a zip_file is provided")
            end
            __init_from_file(self, zip_file, true)
        elseif create then
            __init_empty(self)
        else
            __init_from_existing(self)
        end
        return self
    end
    setmetatable(CrayonExperiment, mt)

    -- Initialisation
    __init_empty = function(self)
        local query = "/data"
        local r = requests.post{
            url = self.client.url..query,
            data = json.encode(self.xp_name),
            headers = json_headers
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
    end

    __init_from_existing = function(self)
        local query = "/data"
        local r = requests.get{
            url = self.client.url..query,
            params = {xp = self.xp_name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        local content = r.json()
        __update_steps(content["scalars"], self.scalar_steps, self.get_scalar_values)
        __update_steps(content["histograms"], self.hist_steps, self.get_histogram_values)
    end

    __init_from_file = function(self, zip_file, force)
        local file = io.open(zip_file, "rb")
        local content = file:read("*all")
        file:close()

        local query = "/backup"
        local r = requests.post{
            url = self.client.url..query,
            params = {xp=self.xp_name, force=force},
            data = content,
            headers = zip_headers
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
    end

    -- Scalar methods
    function CrayonExperiment:get_scalar_names()
        return __get_name_list(self, "scalars")
    end

    function CrayonExperiment:add_scalar_value(name, value, wall_time, step)
        if not wall_time then
            wall_time = socket.gettime()
        end
        if not step then
            step = self.scalar_steps[name]
        end
        self.scalar_steps[name] = step + 1

        local query = "/data/scalars"
        local r = requests.post{
            url = self.client.url..query,
            params = {xp=self.xp_name, name=name},
            data = {wall_time, step, value},
            headers = json_headers
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
    end

    function CrayonExperiment:add_scalar_dict(data, wall_time, step)
        for nane, value in pairs(data) do
            if type(name) ~= "string" then
                error("Scalar name should be a string, got: "..name..".")
            end
            self.add_scalar_value(name, value, wall_time, step)
        end
    end

    function CrayonExperiment:get_scalar_values(name)
        query = "/data/scalars"
        local r = requests.get{
            url = self.client.url..query,
            params = {xp=self.xp_name, name=name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        return r.json()
    end

    -- Histogram methods
    function CrayonExperiment:get_histogram_names()
        return __get_name_list(self, "histograms")
    end

    function CrayonExperiment:add_histogram_value(name, hist, tobuild, wall_time, step)
        if not wall_time then
            wall_time = socket.gettime()
        end
        if not step then
            step = self.hist_steps[name]
        end
        self.hist_steps[name] = step + 1

        __check_histogram_data(hist, tobuild)

        local query = "/data/histograms"
        local r = requests.post{
            url = self.client.url..query,
            params = {xp=self.xp_name, name=name},
            data = {wall_time, step, hist},
            headers = json_headers
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
    end

    function CrayonExperiment:get_histogram_values(name)
        query = "/data/histograms"
        local r = requests.get{
            url = self.client.url..query,
            params = {xp=self.xp_name, name=name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        return r.json()
    end

    __check_histogram_data = function(data, tobuild)
        local required = {bucket=1, bucket_limit=1, max=1, min=1, num=1}
        local optionnal = {sum=1, sum_squares=1}

        if tobuild then
            if #data == 0 then
                error("When building the histogram should be provided as a list in a table.")
            end
        else
            for key,_ in pairs(required) do
                if not data[key] then
                    error("Built histogram is missing argument: "..key)
                end
            end
            for key,_ in pairs(data) do
                if (not required[key]) and (not optionnal[key]) then
                    error("Built histogram has extra parameter: "..key)
                end
            end
        end
    end

    -- Backup methods
    function CrayonExperiment:to_zip(filename)
        filename = filename or "backup_"..self.xp_name.."_"..tostring(socket.gettime())..".zip"
        local query = "/backup"
        local r = requests.get{
            url = self.client.url..query,
            params = {xp=self.xp_name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end

        local f = io.open(filename, "w")
        f:write(r.text)
        f:close()
    end

    -- helper methods
    __get_name_list = function(self, element_type)
        local query = "/data"
        local r = requests.get{
            url = self.client.url..query,
            params = {xp=self.xp_name}
        }
        if r.status_code ~= 200 then
            local msg = "Something went wrong. Server sent: "..r.text.."."
            error(msg)
        end
        return r.json()[element_type]
    end

    __update_steps = function(self, elements, steps_table, eval_function)
        for _, element in pairs(elements) do
            print("element", element)
            values = eval_function(element)
            print("values", values)
            if #values > 0 then
                steps_table[element] = values[#values][1] + 1
            end
        end
    end
end

return {
    CrayonClient= CrayonClient
}
