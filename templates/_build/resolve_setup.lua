-- Climb Setup: run from Workspace > Scripts > Climb Setup inside DaVinci Resolve (works in the free version).
-- Builds the "Climb Templates" project (UHD 3840x2160, 25fps, Rec.709), one test timeline per brand with every
-- Climb title on it, renders small PNG test frames of each title, and saves and exports the Climb render presets.
-- Writes a log to /Users/Shared/Climb-Resolve/out/logs/setup.log.

local ROOT = "/Users/Shared/Climb-Resolve/out"
local BRANDS = { "ClimbUK", "ClimbGroup", "Climb27" }
local TITLES = { "Lower Third", "Lower Third Festival", "Title Card", "End Card", "Sticker" }
local MODE = os.getenv("CLIMB_MODE") or "all"        -- not passed by Resolve; edit here if needed
local FPS = 25

bmd.createdir(ROOT .. "/logs")
local log = io.open(ROOT .. "/logs/setup.log", "w")
local function say(...)
    local parts = {}
    for i = 1, select("#", ...) do parts[#parts + 1] = tostring(select(i, ...)) end
    local s = table.concat(parts, " ")
    log:write(s, "\n"); log:flush(); print(s)
end

local resolve = resolve or (app and app:GetResolve()) or (Resolve and Resolve())   -- the free version only gives the resolve global
local pm = resolve:GetProjectManager()
say("Resolve", resolve:GetVersionString(), resolve:GetProductName())

-- project -------------------------------------------------------------------------------------------------------
local NAME = "Climb Templates"
local project = pm:LoadProject(NAME)
if project then
    pm:CloseProject(project)
    pm:DeleteProject(NAME)
end
project = pm:CreateProject(NAME)
say("project", project and project:GetName())

-- in order: the playback rate is only accepted once the timeline rate and monitor format agree with it
local settings = {
    { "timelineResolutionWidth", "3840" }, { "timelineResolutionHeight", "2160" },
    { "timelineOutputResolutionWidth", "3840" }, { "timelineOutputResolutionHeight", "2160" },
    { "timelineFrameRate", "25" }, { "videoMonitorFormat", "HD 1080p 25" }, { "timelinePlaybackFrameRate", "25" },
    { "colorScienceMode", "davinciYRGB" },
    { "colorSpaceTimeline", "Rec.709 Gamma 2.4" }, { "colorSpaceOutput", "Rec.709 Gamma 2.4" },
}
for _, kv in ipairs(settings) do
    say("set", kv[1], kv[2], project:SetSetting(kv[1], kv[2]), "->", project:GetSetting(kv[1]))
end

-- render formats and codecs ---------------------------------------------------------------------------------------
local formats = project:GetRenderFormats()
for f, ext in pairs(formats) do say("format", f, ext) end
local function codecs(fmt)
    local out = {}
    for desc, name in pairs(project:GetRenderCodecs(fmt) or {}) do
        out[#out + 1] = { desc = desc, name = name }
        say("codec", fmt, desc, name)
    end
    return out
end
local function find_codec(fmt, patterns)
    local list = codecs(fmt)
    for _, p in ipairs(patterns) do
        for _, c in ipairs(list) do
            if c.desc:lower():find(p:lower(), 1, true) or c.name:lower():find(p:lower(), 1, true) then return c.name end
        end
    end
end

-- frames <-> timecode -------------------------------------------------------------------------------------------
local function tc(frame)
    local f = frame % FPS
    local s = math.floor(frame / FPS)
    return string.format("%02d:%02d:%02d:%02d", math.floor(s / 3600), math.floor(s / 60) % 60, s % 60, f)
end

-- timelines with every title --------------------------------------------------------------------------------------
local mp = project:GetMediaPool()
local found = {}
for _, brand in ipairs(BRANDS) do
    local tl = mp:CreateEmptyTimeline(brand .. " titles")
    project:SetCurrentTimeline(tl)
    local start = tl:GetStartFrame()
    local at = start
    for _, t in ipairs(TITLES) do
        local name = brand .. " " .. t
        tl:SetCurrentTimecode(tc(at))
        local item = tl:InsertFusionTitleIntoTimeline(name)
        if item then
            local s, e = item:GetStart(), item:GetEnd()
            local comp = item:GetFusionCompByIndex(1)
            local tools = {}
            if comp then
                for _, tool in pairs(comp:GetToolList(false) or {}) do
                    tools[#tools + 1] = tool:GetAttrs().TOOLS_RegID .. ":" .. tool.Name
                end
            end
            say("title OK", name, "start", s, "end", e, "dur", item:GetDuration(), "comps", item:GetFusionCompCount(),
                "tools", table.concat(tools, ","))
            found[#found + 1] = { brand = brand, name = name, tl = tl, s = s - start, e = e - start }
            at = e
        else
            say("title MISSING", name)
        end
    end
end
project:SetCurrentTimeline(project:GetTimelineByIndex(1))
pm:SaveProject()

-- test renders: a 960x540 PNG sequence (with alpha) of every title --------------------------------------------------
local png = formats["png"] and "png" or (formats["PNG"] and "PNG")
local tif = formats["tif"] and "tif" or "TIFF"
local stillfmt = png or tif
local stillcodec = find_codec(stillfmt, { "RGBA", "RGB 8", "8 bit", "RGB" })
say("still format", stillfmt, stillcodec)
project:DeleteAllRenderJobs()
resolve:OpenPage("deliver")
local jobs = {}
for _, f in ipairs(found) do
    project:SetCurrentTimeline(f.tl)
    local st = f.tl:GetStartFrame()
    project:SetCurrentRenderFormatAndCodec(stillfmt, stillcodec)
    local ok = project:SetRenderSettings({
        SelectAllFrames = false, MarkIn = st + f.s, MarkOut = st + f.e - 1,
        TargetDir = ROOT .. "/test-renders/" .. f.name:gsub(" ", "_"), CustomName = f.name:gsub(" ", "_") .. "_",
        FormatWidth = 960, FormatHeight = 540, ExportVideo = true, ExportAudio = false, ExportAlpha = true,
    })
    local id = project:AddRenderJob()
    say("job", f.name, ok, id)
    jobs[#jobs + 1] = id
end
-- one full-size frame of each title at 1.5s, to check type sizes against the stills
for _, f in ipairs(found) do
    project:SetCurrentTimeline(f.tl)
    local st = f.tl:GetStartFrame()
    project:SetCurrentRenderFormatAndCodec(stillfmt, stillcodec)
    project:SetRenderSettings({
        SelectAllFrames = false, MarkIn = st + f.s + 37, MarkOut = st + f.s + 37,
        TargetDir = ROOT .. "/test-renders/_4K", CustomName = f.name:gsub(" ", "_") .. "_4K_",
        FormatWidth = 3840, FormatHeight = 2160, ExportVideo = true, ExportAudio = false, ExportAlpha = true,
    })
    jobs[#jobs + 1] = project:AddRenderJob()
end
project:StartRendering()
while project:IsRenderingInProgress() do bmd.wait(1) end
for _, id in ipairs(jobs) do
    local st = project:GetRenderJobStatus(id) or {}
    say("render", id, st.JobStatus, st.CompletionPercentage, st.Error or "")
end
project:DeleteAllRenderJobs()

-- render presets ----------------------------------------------------------------------------------------------------
bmd.createdir(ROOT .. "/render-presets")
-- exact name: a substring match on "ProRes4444" also finds ProRes 4444 XQ
local prores
for _, c in ipairs(codecs("mov")) do if c.name == "ProRes4444" then prores = c.name end end
local h264 = find_codec("mp4", { "H.264", "H264" })
say("codecs chosen", prores, h264)
project:SetCurrentTimeline(project:GetTimelineByIndex(1))
local presets = {
    { name = "Climb Master ProRes 4444 alpha UHD25", fmt = "mov", codec = prores,
      s = { FormatWidth = 3840, FormatHeight = 2160, ExportAlpha = true, ExportAudio = true, AudioCodec = "lpcm",
            AudioSampleRate = 48000, AudioBitDepth = 24 } },
    { name = "Climb YouTube H264 16x9 UHD25", fmt = "mp4", codec = h264,
      s = { FormatWidth = 3840, FormatHeight = 2160, VideoQuality = 45000, ExportAudio = true, AudioCodec = "aac",
            AudioSampleRate = 48000, NetworkOptimization = true } },
    { name = "Climb Social H264 9x16 2160x3840 25", fmt = "mp4", codec = h264,
      s = { FormatWidth = 2160, FormatHeight = 3840, VideoQuality = 35000, ExportAudio = true, AudioCodec = "aac",
            AudioSampleRate = 48000, NetworkOptimization = true } },
}
for _, p in ipairs(presets) do
    project:DeleteRenderPreset(p.name)
    local a = project:SetCurrentRenderFormatAndCodec(p.fmt, p.codec)
    p.s.SelectAllFrames = true
    p.s.ExportVideo = true
    p.s.FrameRate = 25
    p.s.TargetDir = os.getenv("HOME") .. "/Movies"
    -- one key at a time, so a key this version rejects is logged and the rest still apply
    local b = true
    for k, v in pairs(p.s) do
        local ok = project:SetRenderSettings({ [k] = v })
        if not ok then say("preset", p.name, "rejected", k, v); b = false end
    end
    local c = project:SaveAsNewRenderPreset(p.name)
    local d = resolve:ExportRenderPreset(p.name, ROOT .. "/render-presets/" .. p.name .. ".xml")
    say("preset", p.name, "format", a, "settings", b, "saved", c, "exported", d)
end
for _, p in ipairs(project:GetRenderPresetList() or {}) do
    say("preset list", type(p) == "table" and (p.PresetName or p.Name or "?") or p)
end

pm:SaveProject()
bmd.createdir(ROOT .. "/project")
say("export project", pm:ExportProject(NAME, ROOT .. "/project/Climb Templates.drp", false))
say("done")
log:close()
