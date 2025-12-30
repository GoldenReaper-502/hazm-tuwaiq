using Microsoft.EntityFrameworkCore;
using SmartSafety.API.Models;

namespace SmartSafety.API.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    
    public DbSet<Camera> Cameras { get; set; }
    public DbSet<Incident> Incidents { get; set; }
    public DbSet<Detection> Detections { get; set; }
    public DbSet<ChatMessage> ChatMessages { get; set; }
    public DbSet<RiskAssessment> RiskAssessments { get; set; }
    public DbSet<Inspection> Inspections { get; set; }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // Seed initial data
        modelBuilder.Entity<Camera>().HasData(
            new Camera 
            { 
                Id = 1, 
                Name = "كاميرا المدخل الرئيسي",
                Url = "rtsp://demo-camera-1",
                Location = "المدخل الرئيسي",
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            },
            new Camera 
            { 
                Id = 2, 
                Name = "كاميرا موقع البناء",
                Url = "rtsp://demo-camera-2",
                Location = "موقع البناء - القسم أ",
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            }
        );
        
        modelBuilder.Entity<Incident>().HasData(
            new Incident
            {
                Id = 1,
                Title = "عدم ارتداء خوذة السلامة",
                Description = "تم رصد عامل بدون خوذة سلامة في منطقة البناء",
                Severity = "high",
                Status = "open",
                ReportedBy = "النظام الآلي",
                Location = "موقع البناء - القسم أ",
                ReportedAt = DateTime.UtcNow
            }
        );
    }
}
