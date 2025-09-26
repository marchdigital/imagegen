# Add this to backend/routes/extended.py

@router.post("/wan25-i2v")
async def generate_wan25_i2v(
    request: Request,
    image_data: str = Form(...),
    prompt: str = Form(...),
    duration: Optional[int] = Form(5),
    resolution: Optional[str] = Form("720p"),
    fps: Optional[int] = Form(30),
    generate_audio: Optional[bool] = Form(True),
    guidance_scale: Optional[float] = Form(7.0),
    motion_strength: Optional[float] = Form(1.0),
    camera_movement: Optional[str] = Form("auto"),
    seed: Optional[int] = Form(None)
):
    """Generate video from image using WAN 2.5 Preview Image-to-Video"""
    try:
        # Validate inputs
        if len(prompt) < 10:
            raise HTTPException(
                status_code=400,
                detail="Prompt must be at least 10 characters long"
            )
        
        if duration < 3 or duration > 10:
            raise HTTPException(
                status_code=400,
                detail="Duration must be between 3 and 10 seconds"
            )
        
        if resolution not in ["720p", "1080p"]:
            raise HTTPException(
                status_code=400,
                detail="Resolution must be either 720p or 1080p"
            )
        
        if fps not in [24, 30, 60]:
            raise HTTPException(
                status_code=400,
                detail="FPS must be 24, 30, or 60"
            )
        
        # Get the provider
        provider = get_provider('fal')
        
        # Call the WAN 2.5 I2V method
        result = await provider.generate_wan25_i2v(
            image_data=image_data,
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            fps=fps,
            generate_audio=generate_audio,
            guidance_scale=guidance_scale,
            motion_strength=motion_strength,
            camera_movement=camera_movement,
            seed=seed
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WAN 2.5 I2V Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )