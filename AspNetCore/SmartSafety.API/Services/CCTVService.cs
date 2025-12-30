using Microsoft.EntityFrameworkCore;
using SmartSafety.API.Data;
using SmartSafety.API.Models;

namespace SmartSafety.API.Services;

public class CCTVService : ICCTVService
{
    private readonly AppDbContext _context;
    private readonly ILogger<CCTVService> _logger;

    public CCTVService(AppDbContext context, ILogger<CCTVService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<IEnumerable<Camera>> GetAllCamerasAsync()
    {
        return await _context.Cameras.ToListAsync();
    }

    public async Task<Camera?> GetCameraByIdAsync(int id)
    {
        return await _context.Cameras.FindAsync(id);
    }

    public async Task<Camera> AddCameraAsync(Camera camera)
    {
        _context.Cameras.Add(camera);
        await _context.SaveChangesAsync();
        return camera;
    }

    public async Task<bool> DeleteCameraAsync(int id)
    {
        var camera = await _context.Cameras.FindAsync(id);
        if (camera == null) return false;
        
        _context.Cameras.Remove(camera);
        await _context.SaveChangesAsync();
        return true;
    }
}
