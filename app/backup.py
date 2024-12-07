from fastapi import FastAPI, Query
import json
import re
from datetime import datetime
import subprocess
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="/app/static"), name="static")


GRASS_DB = "/grassdata"
LOCATION = "nc_spm_08_grass7"
MAPSET = "PERMANENT"
GRASS_BINARY = "grass"

@app.get("/")
def read_root():
    try:
        command = [
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            "g.version"
        ]
        version_result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        grass_version = version_result.stdout.strip() or "Unknown"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "message": "GRASS GIS REST API",
            "grass_version": grass_version,
            "timestamp": current_time
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/grass-info")
def get_grass_info():
    try:
        # สร้างคำสั่ง GRASS GIS
        command = [
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            "g.version",
        ]
        # เรียกใช้งาน GRASS GIS
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}

# @app.get("/grass-command")
# def run_grass_command(command: str = "r.info", parameters: str = ""):
#     try:
#         # สร้างคำสั่ง GRASS GIS
#         grass_command = [
#             GRASS_BINARY,
#             f"{GRASS_DB}/{LOCATION}/{MAPSET}",
#             "--exec",
#             command,
#         ]
#         # เพิ่มพารามิเตอร์ถ้ามี
#         if parameters:
#             grass_command.extend(parameters.split())

#         # รัน GRASS GIS command
#         result = subprocess.run(grass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#         return {
#             "command": f"{command} {parameters}",
#             "output": result.stdout,
#             "error": result.stderr,
#         }
#     except Exception as e:
#         return {"error": str(e)}

@app.get("/grass-command")
def run_grass_command(
    command: str = Query(..., description="GRASS GIS command to run (e.g., 'r.info')"),
    parameters: str = Query("", description="Parameters for the GRASS command, separated by spaces")
):
    try:
        # สร้างคำสั่ง GRASS GIS
        grass_command = [
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            command,
        ]
        # เพิ่มพารามิเตอร์ถ้ามี
        if parameters:
            grass_command.extend(parameters.split())

        # รัน GRASS GIS command
        result = subprocess.run(grass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ประมวลผล stdout
        raw_output = result.stdout.strip()

        # พยายามแปลงผลลัพธ์เป็น JSON
        structured_output = parse_r_info_output(raw_output) if command == "r.info" else {"raw_output": raw_output}

        return {
            "command": f"{command} {parameters}",
            "output": structured_output,
            "error": result.stderr.strip(),
        }
    except Exception as e:
        return {"error": str(e)}


def parse_r_info_output(output: str):
    """แปลงผลลัพธ์จาก r.info ให้อยู่ในรูปแบบ JSON"""
    parsed_output = {}
    lines = output.splitlines()

    # ใช้ regex ดึงข้อมูลระหว่าง | ... |
    for line in lines:
        # ตรวจจับบรรทัดที่มี key และ value
        match = re.match(r"^\s*\|\s*(.+?):\s*(.+?)\s*\|", line)
        if match:
            key, value = match.groups()
            parsed_output[key.strip()] = value.strip()

    # หากไม่มีข้อมูล ให้เก็บ raw_output ไว้
    if not parsed_output:
        parsed_output["raw_output"] = output

    return parsed_output

# r.sim.water - Flood Simulation
# @app.post("/simulate-water")
# def simulate_water(flow_params: dict):
#     """
#     API สำหรับเรียกใช้โมดูล r.sim.water
#     Parameters:
#         flow_params: dict - ค่าพารามิเตอร์ที่ต้องส่งไปให้ r.sim.water
#     Example Input:
#         {
#             "elevation": "elev_lid792_1m",
#             "dx": "elev_lid792_dx",
#             "dy": "elev_lid792_dy",
#             "depth": "water_depth",
#             "disch": "water_discharge",
#             "nwalk": 10000,
#             "rain_value": 100,
#             "niter": 5
#         }
#     """
#     try:
#         # ตรวจสอบพารามิเตอร์ที่จำเป็น
#         required_params = ["elevation", "dx", "dy", "depth", "disch"]
#         for param in required_params:
#             if param not in flow_params:
#                 return {"error": f"Missing required parameter: {param}"}

#         # กำหนดค่า default สำหรับพารามิเตอร์เพิ่มเติม
#         nwalk = flow_params.get("nwalk", 10000)  # จำนวน walkers
#         rain_value = flow_params.get("rain_value", 100)  # ค่าปริมาณน้ำฝน
#         niter = flow_params.get("niter", 5)  # จำนวน iteration

#         # สร้างคำสั่งสำหรับ r.sim.water
#         grass_command = [
#             GRASS_BINARY,
#             f"{GRASS_DB}/{LOCATION}/{MAPSET}",
#             "--exec",
#             "r.sim.water",
#             f"elevation={flow_params['elevation']}",
#             f"dx={flow_params['dx']}",
#             f"dy={flow_params['dy']}",
#             f"depth={flow_params['depth']}",
#             f"disch={flow_params['disch']}",
#             f"nwalk={nwalk}",
#             f"rain_value={rain_value}",
#             f"niter={niter}",
#             "--overwrite"
#         ]

#         # รัน GRASS GIS command
#         result = subprocess.run(grass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#         # ตรวจสอบผลลัพธ์
#         if result.returncode != 0:
#             return {
#                 "error": "Failed to execute r.sim.water",
#                 "command": " ".join(grass_command),
#                 "stderr": result.stderr
#             }

#         # หากสำเร็จ ให้ส่งผลลัพธ์กลับมา
#         return {
#             "message": "Simulation completed successfully.",
#             "command": " ".join(grass_command),
#             "output": result.stdout,
#             "stderr": result.stderr,
#         }

#     except Exception as e:
#         return {"error": str(e)}

# V2
# @app.post("/simulate-water")
# def simulate_water(flow_params: dict):
#     """
#     API สำหรับเรียกใช้ r.sim.water และสร้าง GeoTIFF output
#     """
#     try:
#         # ตรวจสอบพารามิเตอร์ที่จำเป็น
#         required_params = ["elevation", "dx", "dy", "depth", "disch"]
#         for param in required_params:
#             if param not in flow_params:
#                 return {"error": f"Missing required parameter: {param}"}

#         # กำหนดค่า default สำหรับพารามิเตอร์เพิ่มเติม
#         nwalk = flow_params.get("nwalk", 10000)  # จำนวน walkers
#         rain_value = flow_params.get("rain_value", 100)  # ค่าปริมาณน้ำฝน
#         niter = flow_params.get("niter", 5)  # จำนวน iteration

#         # สร้างคำสั่งสำหรับ r.sim.water
#         grass_command = [
#             GRASS_BINARY,
#             f"{GRASS_DB}/{LOCATION}/{MAPSET}",
#             "--exec",
#             "r.sim.water",
#             f"elevation={flow_params['elevation']}",
#             f"dx={flow_params['dx']}",
#             f"dy={flow_params['dy']}",
#             f"depth={flow_params['depth']}",
#             f"disch={flow_params['disch']}",
#             f"nwalk={nwalk}",
#             f"rain_value={rain_value}",
#             f"niter={niter}",
#             "--overwrite"
#         ]

#         # รันคำสั่ง r.sim.water
#         result = subprocess.run(grass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#         # ตรวจสอบว่าคำสั่งสำเร็จ
#         if result.returncode != 0:
#             return {
#                 "error": "Failed to execute r.sim.water",
#                 "command": " ".join(grass_command),
#                 "stderr": result.stderr
#             }

#         # สร้าง GeoTIFF จากผลลัพธ์
#         output_dir = "/app/static"
#         water_depth_tiff = f"{output_dir}/water_depth.tiff"
#         water_discharge_tiff = f"{output_dir}/water_discharge.tiff"

#         # Export water_depth
#         subprocess.run([
#             GRASS_BINARY,
#             f"{GRASS_DB}/{LOCATION}/{MAPSET}",
#             "--exec",
#             "r.out.gdal",
#             f"input={flow_params['depth']}",
#             f"output={water_depth_tiff}",
#             "format=GTiff",
#             "--overwrite"
#         ], check=True)

#         # Export water_discharge
#         subprocess.run([
#             GRASS_BINARY,
#             f"{GRASS_DB}/{LOCATION}/{MAPSET}",
#             "--exec",
#             "r.out.gdal",
#             f"input={flow_params['disch']}",
#             f"output={water_discharge_tiff}",
#             "format=GTiff",
#             "--overwrite"
#         ], check=True)

#         # คืน URL ของไฟล์ GeoTIFF
#         base_url = "http://localhost:8000/static"
#         return {
#             "message": "Simulation completed successfully.",
#             "water_depth_url": f"{base_url}/water_depth.tiff",
#             "water_discharge_url": f"{base_url}/water_discharge.tiff",
#         }

#     except Exception as e:
#         return {"error": str(e)}


@app.post("/simulate-water")
def simulate_water(flow_params: dict):
    """
    API สำหรับเรียกใช้ r.sim.water และสร้าง GeoTIFF output
    """
    try:
        # ตรวจสอบพารามิเตอร์ที่จำเป็น
        required_params = ["elevation", "dx", "dy", "depth", "disch"]
        for param in required_params:
            if param not in flow_params:
                return {"error": f"Missing required parameter: {param}"}

        # กำหนดค่า default สำหรับพารามิเตอร์เพิ่มเติม
        nwalk = flow_params.get("nwalk", 10000)  # จำนวน walkers
        rain_value = flow_params.get("rain_value", 100)  # ค่าปริมาณน้ำฝน
        niter = flow_params.get("niter", 5)  # จำนวน iteration

        # สร้างคำสั่งสำหรับ r.sim.water
        grass_command = [
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            "r.sim.water",
            f"elevation={flow_params['elevation']}",
            f"dx={flow_params['dx']}",
            f"dy={flow_params['dy']}",
            f"depth={flow_params['depth']}",
            f"disch={flow_params['disch']}",
            f"nwalk={nwalk}",
            f"rain_value={rain_value}",
            f"niter={niter}",
            "--overwrite"
        ]

        # รันคำสั่ง r.sim.water
        result = subprocess.run(grass_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ตรวจสอบว่าคำสั่งสำเร็จ
        if result.returncode != 0:
            return {
                "error": "Failed to execute r.sim.water",
                "command": " ".join(grass_command),
                "output": result.stdout,
                "stderr": result.stderr
            }

        # ในกรณีที่คำสั่งสำเร็จ
        success_response = {
            "message": "Simulation completed successfully.",
            "command": " ".join(grass_command),
            "output": result.stdout,
            "stderr": result.stderr,
        }

        # สร้าง GeoTIFF จากผลลัพธ์
        output_dir = "/app/static"
        water_depth_tiff = f"{output_dir}/water_depth.tiff"
        water_discharge_tiff = f"{output_dir}/water_discharge.tiff"

        # Export water_depth
        subprocess.run([
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            "r.out.gdal",
            f"input={flow_params['depth']}",
            f"output={water_depth_tiff}",
            "format=GTiff",
            "--overwrite"
        ], check=True)

        # Export water_discharge
        subprocess.run([
            GRASS_BINARY,
            f"{GRASS_DB}/{LOCATION}/{MAPSET}",
            "--exec",
            "r.out.gdal",
            f"input={flow_params['disch']}",
            f"output={water_discharge_tiff}",
            "format=GTiff",
            "--overwrite"
        ], check=True)

        # คืน URL ของไฟล์ GeoTIFF
        base_url = "http://localhost:8000/static"
        success_response.update({
            "water_depth_url": f"{base_url}/water_depth.tiff",
            "water_discharge_url": f"{base_url}/water_discharge.tiff",
        })

        return success_response

    except Exception as e:
        return {"error": str(e)}
