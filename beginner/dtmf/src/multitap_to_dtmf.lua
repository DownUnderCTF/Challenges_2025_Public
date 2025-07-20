---@diagnostic disable: unused-local

-- Finished
local flag = "ONLYNINETIESKIDSWILLREMEMBERTHIS"
-- Multi Direct
local multi =
	"666 66 555 999 66 444 66 33 8 444 33 7777 55 444 3 7777 9 444 555 555 777 33 6 33 6 22 33 777 8 44 444 7777"
-- Multi with Obscurity
local multi_with_hash =
	"666#66#555#999#66#444#66#33#8#444#33#7777#55#444#3#7777#9#444#555#555#777#33#6#33#6#22#33#777#8#44#444#7777"
-- Challenge String
local chal_str =
	"22472247224724182247224724182106210621062418232923292329241822472247241819791979197924182247224724182174217424182188241819791979197924182174217424182061206120612061241821062106241819791979197924182174241820612061206120612418232924181979197919792418210621062106241821062106210624182061206120612418217421742418224724182174217424182247241820332033241821742174241820612061206124182188241819791979241819791979197924182061206120612061"

local dtmf = {
	["1"] = { low = 697, high = 1209, comb = 1906 },
	["2"] = { low = 697, high = 1336, comb = 2033 },
	["3"] = { low = 697, high = 1477, comb = 2174 },
	["A"] = { low = 697, high = 1633, comb = 2330 },
	["4"] = { low = 770, high = 1209, comb = 1979 },
	["5"] = { low = 770, high = 1336, comb = 2106 },
	["6"] = { low = 770, high = 1477, comb = 2247 },
	["B"] = { low = 770, high = 1633, comb = 2403 },
	["7"] = { low = 852, high = 1209, comb = 2061 },
	["8"] = { low = 852, high = 1336, comb = 2188 },
	["9"] = { low = 852, high = 1477, comb = 2329 },
	["C"] = { low = 852, high = 1633, comb = 2485 },
	["*"] = { low = 941, high = 1209, comb = 2150 },
	["0"] = { low = 941, high = 1336, comb = 2277 },
	["#"] = { low = 941, high = 1477, comb = 2418 },
	["D"] = { low = 941, high = 1633, comb = 2574 },
}

local function make_chal(freqs, str)
	local out = ""
	for i = 1, #str do
		local c = str:sub(i, i)
		out = out .. freqs[c].comb
	end

	local file = io.open("../publish/dtmf.txt", "w")
	if file == nil then
		os.exit(1)
	end
	file:write(out)
	file:close()
end

make_chal(dtmf, multi_with_hash)

-- local function flag_to_multi() end
-- local function get_comb()
-- 	for k, v in pairs(dtmf) do
-- 		print(k, v.low + v.high)
-- 	end
-- end
