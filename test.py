$novaCreateUrl = "https://api-ap-south-mum-1.openstack.acecloudhosting.com:8774/v2.1/servers"

$vmBody = @{
    "server" = @{
        "name" = "my-first-vm"
        "imageRef" = "b3f7de60-758e-46ce-a9f9-d6bfa51aa04f"  # Replace with your image ID
        "flavorRef" = "0003ee89-5d94-42f5-a331-85d2f838bd2e"  # Replace with your flavor ID
        "networks" = @(
            @{ "uuid" = "41e6e97b-b3fe-474e-bb74-dbc7943b1a6c" }  # Replace with your network ID
        )
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod -Uri $novaCreateUrl -Method Post -Headers $headers -Body $vmBody
$response | Format-Table -AutoSize