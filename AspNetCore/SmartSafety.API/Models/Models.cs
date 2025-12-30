using System.ComponentModel.DataAnnotations;

namespace SmartSafety.API.Models;

public class Camera
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;
    
    [Required]
    public string Url { get; set; } = string.Empty;
    
    [MaxLength(500)]
    public string? Location { get; set; }
    
    public bool IsActive { get; set; } = true;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime? LastSnapshot { get; set; }
}

public class Incident
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(300)]
    public string Title { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(50)]
    public string Severity { get; set; } = "medium"; // low, medium, high, critical
    
    [Required]
    [MaxLength(50)]
    public string Status { get; set; } = "open"; // open, investigating, resolved
    
    [MaxLength(200)]
    public string? ReportedBy { get; set; }
    
    [MaxLength(200)]
    public string? Location { get; set; }
    
    public DateTime ReportedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime? ResolvedAt { get; set; }
}

public class Detection
{
    [Key]
    public int Id { get; set; }
    
    public int? CameraId { get; set; }
    
    public string ImagePath { get; set; } = string.Empty;
    
    public string Objects { get; set; } = "[]"; // JSON array
    
    public int ObjectCount { get; set; }
    
    public DateTime DetectedAt { get; set; } = DateTime.UtcNow;
    
    public Camera? Camera { get; set; }
}

public class ChatMessage
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public string SessionId { get; set; } = string.Empty;
    
    [Required]
    public string UserMessage { get; set; } = string.Empty;
    
    public string AssistantResponse { get; set; } = string.Empty;
    
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class RiskAssessment
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(300)]
    public string Title { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(50)]
    public string RiskLevel { get; set; } = "medium";
    
    [MaxLength(200)]
    public string? Assessor { get; set; }
    
    public DateTime AssessedAt { get; set; } = DateTime.UtcNow;
}

public class Inspection
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(300)]
    public string Title { get; set; } = string.Empty;
    
    [MaxLength(500)]
    public string? Location { get; set; }
    
    [MaxLength(200)]
    public string? Inspector { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string Status { get; set; } = "pending";
    
    public string Findings { get; set; } = string.Empty;
    
    public DateTime ScheduledAt { get; set; }
    
    public DateTime? CompletedAt { get; set; }
}
