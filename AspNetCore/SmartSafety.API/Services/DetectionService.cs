using SmartSafety.API.Data;
using SmartSafety.API.Models;

namespace SmartSafety.API.Services;

public class DetectionService : IDetectionService
{
    private readonly AppDbContext _context;
    private readonly ILogger<DetectionService> _logger;

    public DetectionService(AppDbContext context, ILogger<DetectionService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<DetectionResult> DetectObjectsAsync(byte[] imageData)
    {
        // TODO: Implement YOLO or other object detection
        // For now, return mock data
        await Task.Delay(300);
        
        var result = new DetectionResult
        {
            Objects = new List<DetectedObject>
            {
                new DetectedObject 
                { 
                    Class = "person", 
                    Confidence = 0.95,
                    Box = new BoundingBox { X = 100, Y = 150, Width = 200, Height = 300 }
                },
                new DetectedObject 
                { 
                    Class = "hardhat", 
                    Confidence = 0.88,
                    Box = new BoundingBox { X = 120, Y = 150, Width = 80, Height = 60 }
                }
            },
            ObjectCount = 2
        };
        
        return result;
    }

    public async Task<IEnumerable<Detection>> GetRecentDetectionsAsync(int limit = 10)
    {
        return await Task.FromResult(_context.Detections
            .OrderByDescending(d => d.DetectedAt)
            .Take(limit)
            .ToList());
    }
}
