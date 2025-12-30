using Microsoft.AspNetCore.Mvc;
using SmartSafety.API.Services;

namespace SmartSafety.API.Controllers;

[ApiController]
[Route("api/system")]
public class SystemController : ControllerBase
{
    private readonly IAIService _aiService;
    private readonly IConfiguration _configuration;

    public SystemController(IAIService aiService, IConfiguration configuration)
    {
        _aiService = aiService;
        _configuration = configuration;
    }

    [HttpGet("status")]
    [ProducesResponseType(typeof(SystemStatusResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetStatus()
    {
        var status = await _aiService.GetSystemStatusAsync();
        
        var response = new SystemStatusResponse
        {
            LlmAvailable = status.LLMAvailable,
            LlmProvider = status.LLMProvider,
            CctvAvailable = status.CCTVAvailable,
            Version = _configuration["App:Version"] ?? "1.0.0",
            Environment = _configuration["App:Environment"] ?? "Production",
            Timestamp = status.Timestamp
        };
        
        return Ok(response);
    }
}

public class SystemStatusResponse
{
    public bool LlmAvailable { get; set; }
    public string? LlmProvider { get; set; }
    public bool CctvAvailable { get; set; }
    public string Version { get; set; } = "1.0.0";
    public string Environment { get; set; } = "Production";
    public DateTime Timestamp { get; set; }
}
