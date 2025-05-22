import openstack
import traceback

def connect_openstack():
    try:
        conn = openstack.connection.Connection(
            auth_url='https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3',
            token='gAAAAABoFg-rHOrSC_9qdw2WjLyhyI3DoQwHLnf7PChV5yZoG4JxUQRO3QoXrG89l4fk9i8ddWbqH4ucP_5V_kEVCyelG_U5l0drfp2198L2o0LFyywwKJ97x1IPiFZIgh-5W6MFXuIkYNMR5Q8nVzy9oGvPREt1FtNDX8i7fMevcwR-fRvdsn0',
            project_id='a02b14bcfca64e44bd68f2d00d8555b5',
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

def delete_vm(conn, vm_name):
    try:
        # List all servers with the matching name
        servers = [server for server in conn.compute.servers() if server.name == vm_name]
        
        if not servers:
            print(f"❌ VM '{vm_name}' not found.")
            return False
        
        for server in servers:
            print(f"🗑️ Deleting VM '{server.name}' with ID {server.id}...")
            conn.compute.delete_server(server, ignore_missing=False)
            conn.compute.wait_for_delete(server)
            print(f"✅ VM '{server.name}' with ID {server.id} deleted successfully.")
        
        return True
    except Exception as e:
        print(f"❌ Failed to delete VM(s): {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    conn = connect_openstack()
    if conn:
        vm_name = "dev-box"
        success = delete_vm(conn, vm_name)
        if not success:
            print("🚫 VM deletion failed.")
    else:
        print("🚫 Aborting VM deletion due to connection failure.")
