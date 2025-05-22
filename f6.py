import openstack
import traceback
from openstack.exceptions import NotFoundException

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFg-rHOrSC_9qdw2WjLyhyI3DoQwHLnf7PChV5yZoG4JxUQRO3QoXrG89l4fk9i8ddWbqH4ucP_5V_kEVCyelG_U5l0drfp2198L2o0LFyywwKJ97x1IPiFZIgh-5W6MFXuIkYNMR5Q8nVzy9oGvPREt1FtNDX8i7fMevcwR-fRvdsn0',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def get_project_usage(conn):
    try:
        print("📊 Gathering project usage...")

        # Aggregate vCPU and RAM from servers
        servers = list(conn.compute.servers(all_projects=False))
        total_vcpus = 0
        total_ram_mb = 0
        total_gpus = 0  # Assuming GPU info is available via flavor extra specs or metadata

        for server in servers:
            flavor_id = server.flavor.get('id')
            try:
                flavor = conn.compute.get_flavor(flavor_id)
            except NotFoundException:
                print(f"⚠️ Flavor '{flavor_id}' not found for server '{server.id}', skipping this server.")
                continue
            except Exception as e:
                print(f"⚠️ Unexpected error fetching flavor '{flavor_id}' for server '{server.id}': {e}")
                continue

            total_vcpus += flavor.vcpus
            total_ram_mb += flavor.ram

            # GPU counting depends on flavor extra_specs or metadata
            gpu_count = 0
            try:
                extra_specs = flavor.extra_specs if hasattr(flavor, 'extra_specs') else {}
                gpu_count = int(extra_specs.get('resources:VGPU', 0))
            except Exception:
                # If any error parsing GPU count, just ignore and assume 0
                gpu_count = 0
            total_gpus += gpu_count

        # Aggregate volume size in GB
        volumes = list(conn.block_storage.volumes(details=True))
        total_volume_gb = sum(volume.size for volume in volumes if volume.status in ['available', 'in-use'])

        print(f"✅ Usage Summary:")
        print(f"   - Total vCPUs: {total_vcpus}")
        print(f"   - Total RAM (MB): {total_ram_mb}")
        print(f"   - Total GPUs: {total_gpus}")
        print(f"   - Total Volume Size (GB): {total_volume_gb}")

        return {
            "vcpus": total_vcpus,
            "ram_mb": total_ram_mb,
            "gpus": total_gpus,
            "volume_gb": total_volume_gb
        }
    except Exception as e:
        print(f"❌ Failed to get usage: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    conn = connect_openstack()
    if conn:
        usage = get_project_usage(conn)
        if not usage:
            print("🚫 Usage query failed.")
    else:
        print("🚫 Aborting usage query due to connection failure.")


