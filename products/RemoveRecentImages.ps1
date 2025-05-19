# Create a file called RemoveRecentImages.ps1 with this content
$minutesAgo = 20
$cutoffTime = (Get-Date).AddMinutes(-$minutesAgo)

Write-Host "Looking for Docker images created in the last $minutesAgo minutes..." -ForegroundColor Yellow

# Get all images
$images = docker images --format "{{.ID}};{{.Repository}};{{.Tag}};{{.CreatedAt}}"

foreach ($image in $images) {
    # Split the output using semicolon as delimiter
    $parts = $image.Split(";")

    if ($parts.Length -ge 4) {
        $imageId = $parts[0]
        $repository = $parts[1]
        $tag = $parts[2]
        $createdAtStr = $parts[3]

        try {
            # Parse the creation time
            $createdAt = [DateTime]::Parse($createdAtStr)

            # Check if image was created within the last 20 minutes
            if ($createdAt -gt $cutoffTime) {
                Write-Host "Removing image $repository`:$tag (ID: $imageId) created at $createdAt" -ForegroundColor Cyan
                docker rmi -f $imageId
            }
        }
        catch {
            Write-Host "Error processing image $imageId`: $_" -ForegroundColor Red
        }
    }
}

Write-Host "Cleanup complete!" -ForegroundColor Green