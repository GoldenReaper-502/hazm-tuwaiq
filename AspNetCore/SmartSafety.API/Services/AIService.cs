using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace SmartSafety.API.Services;

public class AIService : IAIService
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<AIService> _logger;
    private readonly string? _geminiKey;
    private readonly string? _openaiKey;
    private readonly string _provider;

    public AIService(IConfiguration configuration, ILogger<AIService> logger)
    {
        _configuration = configuration;
        _logger = logger;
        _geminiKey = _configuration["AI:GeminiApiKey"];
        _openaiKey = _configuration["AI:OpenAIApiKey"];
        _provider = _configuration["AI:Provider"] ?? "gemini";
    }

    public async Task<AIResponse> GenerateResponseAsync(string message, string sessionId)
    {
        try
        {
            // Priority: OpenAI -> Gemini
            if (!string.IsNullOrEmpty(_openaiKey))
            {
                return await GenerateOpenAIResponseAsync(message);
            }
            else if (!string.IsNullOrEmpty(_geminiKey) && _provider == "gemini")
            {
                return await GenerateGeminiResponseAsync(message);
            }
            
            // No API key configured
            var errorMsg = "❌ No AI API key configured.\n\n";
            errorMsg += "📋 To fix this:\n";
            errorMsg += "1. Set environment variable: export OPENAI_API_KEY=\"sk-...\"\n";
            errorMsg += "2. Or add to appsettings.json: \"AI:OpenAIApiKey\": \"sk-...\"\n\n";
            errorMsg += "🔑 Get your key: https://platform.openai.com/api-keys";
            
            return new AIResponse
            {
                Error = errorMsg
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "خطأ في توليد رد AI");
            return new AIResponse
            {
                Error = $"خطأ في AI: {ex.Message}"
            };
        }
    }

    private async Task<AIResponse> GenerateGeminiResponseAsync(string message)
    {
        // TODO: Implement Google Gemini API integration
        // For now, return a mock response
        await Task.Delay(500); // Simulate API call
        
        return new AIResponse
        {
            Answer = $"أنا مساعد السلامة الذكية. رسالتك: {message}\\n\\nهذه استجابة تجريبية. يرجى تكوين Gemini API للحصول على ردود حقيقية.",
            Sources = new List<string> { "Google Gemini (Mock)" },
            Confidence = 0.85
        };
    }

    private async Task<AIResponse> GenerateOpenAIResponseAsync(string message)
    {
        try
        {
            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_openaiKey}");
            
            var systemPrompt = @"You are Smart Safety AI Assistant - an expert in workplace safety and ISO 45001:2018.
Provide concise, actionable safety advice in Arabic or English based on the user's language.
Focus on: incident prevention, risk assessment, compliance, and safety culture.";

            var requestBody = new
            {
                model = _configuration["AI:OpenAIModel"] ?? "gpt-4o-mini",
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = message }
                },
                max_tokens = 600,
                temperature = 0.3
            };
            
            var response = await httpClient.PostAsJsonAsync(
                "https://api.openai.com/v1/chat/completions",
                requestBody
            );
            
            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync();
                _logger.LogError("OpenAI API Error: {Error}", error);
                throw new Exception($"OpenAI API returned {response.StatusCode}");
            }
            
            var result = await response.Content.ReadFromJsonAsync<OpenAIResponse>();
            
            return new AIResponse
            {
                Answer = result?.Choices?[0]?.Message?.Content ?? "No response from AI",
                Sources = new List<string> { $"OpenAI {_configuration["AI:OpenAIModel"]}" },
                Confidence = 0.90
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling OpenAI API");
            throw;
        }
    }
    
    public async Task<SystemStatus> GetSystemStatusAsync()
    {
        await Task.CompletedTask;
        
        bool llmAvailable = !string.IsNullOrEmpty(_geminiKey) || !string.IsNullOrEmpty(_openaiKey);
        string? provider = null;
        
        if (!string.IsNullOrEmpty(_openaiKey))
            provider = "OpenAI";
        else if (!string.IsNullOrEmpty(_geminiKey))
            provider = "Google Gemini";
        
        return new SystemStatus
        {
            LLMAvailable = llmAvailable,
            LLMProvider = provider,
            CCTVAvailable = true
        };
    }
}

// OpenAI API Response Models
public class OpenAIResponse
{
    public List<OpenAIChoice>? Choices { get; set; }
}

public class OpenAIChoice
{
    public OpenAIMessage? Message { get; set; }
}

public class OpenAIMessage
{
    public string? Content { get; set; }
}
