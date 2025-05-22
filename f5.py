import openstack
import traceback

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
             auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFg-rHOrSC_9qdw2WjLyhyI3DoQwHLnf7PChV5yZoG4JxUQRO3QoXrG89l4fk9i8ddWbqH4ucP_5V_kEVCyelG_U5l0drfp2198L2o0LFyywwKJ97x1IPiFZIgh-5W6MFXuIkYNMR5Q8nVzy9oGvPREt1FtNDX8i7fMevcwR-fRvdsn0',
            region_name='ap-south-mum-1',
            identity_interface='public',
            auth_type='token'
        )
        conn.authorize()  # Force authentication to verify credentials
        print("✅ Connected to OpenStack successfully.")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to OpenStack:\n{e}")
        traceback.print_exc()
        return None

def create_volume(conn, volume_name, size_gb):
    try:
        print(f"💾 Creating volume '{volume_name}' of size {size_gb} GB...")
        volume = conn.block_storage.create_volume(
            name=volume_name,
            size=size_gb
        )
        conn.block_storage.wait_for_status(volume, status='available', failures=['error'], interval=5, wait=300)
        print(f"✅ Volume '{volume_name}' created successfully with ID: {volume.id}")
        return volume
    except Exception as e:
        print(f"❌ Failed to create volume: {e}")
        traceback.print_exc()
        return None

def delete_volume(conn, volume_name):
    try:
        volume = conn.block_storage.find_volume(volume_name)
        if not volume:
            print(f"❌ Volume '{volume_name}' not found.")
            return False

        print(f"🗑️ Deleting volume '{volume_name}'...")
        conn.block_storage.delete_volume(volume, ignore_missing=False)
        conn.block_storage.wait_for_delete(volume)
        print(f"✅ Volume '{volume_name}' deleted successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to delete volume: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    conn = connect_openstack()
    if conn:
        volume_name = "data-disk"
        size_gb = 100

        vol = create_volume(conn, volume_name, size_gb)
        if not vol:
            print("🚫 Volume creation failed.")

        # Uncomment to delete volume
        # success = delete_volume(conn, volume_name)
        # if not success:
        #     print("🚫 Volume deletion failed.")
    else:
        print("🚫 Aborting volume operation due to connection failure.")
