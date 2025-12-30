using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SmartSafety.API.Data;
using SmartSafety.API.Models;

namespace SmartSafety.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class IncidentsController : ControllerBase
{
    private readonly AppDbContext _context;

    public IncidentsController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll([FromQuery] string? status = null)
    {
        var query = _context.Incidents.AsQueryable();
        
        if (!string.IsNullOrEmpty(status))
            query = query.Where(i => i.Status == status);
        
        var incidents = await query.OrderByDescending(i => i.ReportedAt).ToListAsync();
        return Ok(incidents);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        var incident = await _context.Incidents.FindAsync(id);
        if (incident == null)
            return NotFound();
        
        return Ok(incident);
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] IncidentRequest request)
    {
        var incident = new Incident
        {
            Title = request.Title,
            Description = request.Description,
            Severity = request.Severity ?? "medium",
            Status = "open",
            ReportedBy = request.ReportedBy,
            Location = request.Location
        };
        
        _context.Incidents.Add(incident);
        await _context.SaveChangesAsync();
        
        return CreatedAtAction(nameof(GetById), new { id = incident.Id }, incident);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, [FromBody] IncidentRequest request)
    {
        var incident = await _context.Incidents.FindAsync(id);
        if (incident == null)
            return NotFound();
        
        incident.Title = request.Title;
        incident.Description = request.Description;
        incident.Severity = request.Severity ?? incident.Severity;
        incident.Status = request.Status ?? incident.Status;
        
        if (request.Status == "resolved" && incident.ResolvedAt == null)
            incident.ResolvedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        return Ok(incident);
    }
}

public class IncidentRequest
{
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? Severity { get; set; }
    public string? Status { get; set; }
    public string? ReportedBy { get; set; }
    public string? Location { get; set; }
}
