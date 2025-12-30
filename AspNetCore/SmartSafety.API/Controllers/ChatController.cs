using Microsoft.AspNetCore.Mvc;
using SmartSafety.API.Data;
using SmartSafety.API.Models;
using SmartSafety.API.Services;

namespace SmartSafety.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly IAIService _aiService;
    private readonly AppDbContext _context;
    private readonly ILogger<ChatController> _logger;

    public ChatController(IAIService aiService, AppDbContext context, ILogger<ChatController> logger)
    {
        _aiService = aiService;
        _context = context;
        _logger = logger;
    }

    [HttpPost]
    [ProducesResponseType(typeof(ChatResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(Microsoft.AspNetCore.Mvc.ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(Microsoft.AspNetCore.Mvc.ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> Chat([FromBody] ChatRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Message))
        {
            return Problem(
                statusCode: StatusCodes.Status400BadRequest,
                title: "Invalid Request",
                detail: "Message is required and cannot be empty"
            );
        }

        try
        {
            var response = await _aiService.GenerateResponseAsync(request.Message, request.SessionId);
            
            if (response.Error != null)
            {
                return Problem(
                    statusCode: StatusCodes.Status500InternalServerError,
                    title: "AI Service Error",
                    detail: response.Error
                );
            }
            
            // Save to database
            var chatMessage = new ChatMessage
            {
                SessionId = request.SessionId,
                UserMessage = request.Message,
                AssistantResponse = response.Answer ?? "No response"
            };
            
            _context.ChatMessages.Add(chatMessage);
            await _context.SaveChangesAsync();
            
            var chatResponse = new ChatResponse
            {
                Id = chatMessage.Id,
                SessionId = request.SessionId,
                UserMessage = request.Message,
                AssistantResponse = response.Answer ?? string.Empty,
                Sources = response.Sources,
                Confidence = response.Confidence,
                Timestamp = chatMessage.Timestamp
            };
            
            return Ok(chatResponse);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat request");
            return Problem(
                statusCode: StatusCodes.Status500InternalServerError,
                title: "Internal Server Error",
                detail: "An error occurred while processing your request"
            );
        }
    }
    
    [HttpGet("history/{sessionId}")]
    public async Task<IActionResult> GetHistory(string sessionId)
    {
        var messages = await Task.FromResult(_context.ChatMessages
            .Where(m => m.SessionId == sessionId)
            .OrderBy(m => m.Timestamp)
            .ToList());
        
        return Ok(messages);
    }
}

public class ChatRequest
{
    public required string Message { get; set; }
    public required string SessionId { get; set; }
}

public class ChatResponse
{
    public int Id { get; set; }
    public string SessionId { get; set; } = string.Empty;
    public string UserMessage { get; set; } = string.Empty;
    public string AssistantResponse { get; set; } = string.Empty;
    public List<string> Sources { get; set; } = new();
    public double Confidence { get; set; }
    public DateTime Timestamp { get; set; }
}
