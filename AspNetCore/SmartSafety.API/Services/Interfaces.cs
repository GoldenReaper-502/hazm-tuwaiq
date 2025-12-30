namespace SmartSafety.API.Services;

public interface IAIService
{
    Task<AIResponse> GenerateResponseAsync(string message, string sessionId);
    Task<SystemStatus> GetSystemStatusAsync();
}

public interface ICCTVService
{
    Task<IEnumerable<Models.Camera>> GetAllCamerasAsync();
    Task<Models.Camera?> GetCameraByIdAsync(int id);
    Task<Models.Camera> AddCameraAsync(Models.Camera camera);
    Task<bool> DeleteCameraAsync(int id);
}

public interface IDetectionService
{
    Task<DetectionResult> DetectObjectsAsync(byte[] imageData);
    Task<IEnumerable<Models.Detection>> GetRecentDetectionsAsync(int limit = 10);
}

public class AIResponse
{
    public string Answer { get; set; } = string.Empty;
    public List<string> Sources { get; set; } = new();
    public double Confidence { get; set; }
    public string? Error { get; set; }
}

public class SystemStatus
{
    public bool LLMAvailable { get; set; }
    public string? LLMProvider { get; set; }
    public bool CCTVAvailable { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class DetectionResult
{
    public List<DetectedObject> Objects { get; set; } = new();
    public int ObjectCount { get; set; }
    public DateTime DetectedAt { get; set; } = DateTime.UtcNow;
}

public class DetectedObject
{
    public string Class { get; set; } = string.Empty;
    public double Confidence { get; set; }
    public BoundingBox Box { get; set; } = new();
}

public class BoundingBox
{
    public double X { get; set; }
    public double Y { get; set; }
    public double Width { get; set; }
    public double Height { get; set; }
}
