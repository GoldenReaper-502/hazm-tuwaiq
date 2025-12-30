using Microsoft.AspNetCore.Mvc;
using SmartSafety.API.Models;
using SmartSafety.API.Services;

namespace SmartSafety.API.Controllers;

[ApiController]
[Route("api/cctv")]
public class CCTVController : ControllerBase
{
    private readonly ICCTVService _cctvService;
    private readonly ILogger<CCTVController> _logger;

    public CCTVController(ICCTVService cctvService, ILogger<CCTVController> logger)
    {
        _cctvService = cctvService;
        _logger = logger;
    }

    [HttpGet("cameras")]
    public async Task<IActionResult> GetAllCameras()
    {
        var cameras = await _cctvService.GetAllCamerasAsync();
        return Ok(cameras);
    }

    [HttpGet("cameras/{id}")]
    public async Task<IActionResult> GetCamera(int id)
    {
        var camera = await _cctvService.GetCameraByIdAsync(id);
        if (camera == null)
            return NotFound(new { error = "الكاميرا غير موجودة" });
        
        return Ok(camera);
    }

    [HttpPost("cameras")]
    public async Task<IActionResult> AddCamera([FromBody] CameraRequest request)
    {
        var camera = new Camera
        {
            Name = request.Name,
            Url = request.Url,
            Location = request.Location,
            IsActive = true
        };
        
        var created = await _cctvService.AddCameraAsync(camera);
        return CreatedAtAction(nameof(GetCamera), new { id = created.Id }, created);
    }

    [HttpDelete("cameras/{id}")]
    public async Task<IActionResult> DeleteCamera(int id)
    {
        var result = await _cctvService.DeleteCameraAsync(id);
        if (!result)
            return NotFound(new { error = "الكاميرا غير موجودة" });
        
        return Ok(new { message = "تم حذف الكاميرا بنجاح" });
    }
}

public class CameraRequest
{
    public string Name { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
    public string? Location { get; set; }
}
