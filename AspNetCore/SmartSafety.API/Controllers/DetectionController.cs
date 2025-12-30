using Microsoft.AspNetCore.Mvc;
using SmartSafety.API.Services;

namespace SmartSafety.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DetectionController : ControllerBase
{
    private readonly IDetectionService _detectionService;
    private readonly ILogger<DetectionController> _logger;

    public DetectionController(IDetectionService detectionService, ILogger<DetectionController> logger)
    {
        _detectionService = detectionService;
        _logger = logger;
    }

    [HttpPost("detect")]
    public async Task<IActionResult> Detect([FromForm] IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest(new { error = "يرجى رفع صورة" });

        using var memoryStream = new MemoryStream();
        await file.CopyToAsync(memoryStream);
        var imageData = memoryStream.ToArray();

        var result = await _detectionService.DetectObjectsAsync(imageData);
        
        return Ok(new
        {
            objects = result.Objects,
            object_count = result.ObjectCount,
            detected_at = result.DetectedAt
        });
    }

    [HttpGet("recent")]
    public async Task<IActionResult> GetRecentDetections([FromQuery] int limit = 10)
    {
        var detections = await _detectionService.GetRecentDetectionsAsync(limit);
        return Ok(detections);
    }
}
