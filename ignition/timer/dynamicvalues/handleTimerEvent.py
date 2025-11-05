def handleTimerEvent():
	# ---------------------------------------------------------------------------
	# Varun Beverages Energy Monitoring Simulation Script
	# Location: Project > Gateway Event Scripts > Timer Script
	# Execute every 1000 ms (1 second)
	# ---------------------------------------------------------------------------
	
	import system, random
	from java.util import Calendar
	
	logger = system.util.getLogger("EnergySim")
	
	BASE_PATH = "[default]Varun_Beverages_Energy_Monitoring/"
	
	# -----------------------------
	# Utility functions
	# -----------------------------
	def rand(min_val, max_val):
		return round(random.uniform(min_val, max_val), 2)
	
	def get_hour_factor():
		"""Return multiplier based on day/night hours"""
		hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
		if 7 <= hour <= 18:
			return 1.0
		elif 18 < hour <= 22:
			return 0.7
		else:
			return 0.4
	
	# -----------------------------
	# Energy Sources Simulation
	# -----------------------------
	def simulate_energy_sources():
		try:
			# Solar
			solar_factor = get_hour_factor()
			solar_power = rand(50, 300) * solar_factor
			solar_voltage = rand(400, 450)
			solar_current = round(solar_power / solar_voltage * 1000, 2)
			solar_eff = rand(80, 95)
			irradiance = rand(500, 1000) * solar_factor
			panel_temp = rand(30, 55)
			system.tag.writeBlocking([
				BASE_PATH + "Energy_Sources/Solar_Panel/Power_kW",
				BASE_PATH + "Energy_Sources/Solar_Panel/Voltage_V",
				BASE_PATH + "Energy_Sources/Solar_Panel/Current_A",
				BASE_PATH + "Energy_Sources/Solar_Panel/Irradiance_Wm2",
				BASE_PATH + "Energy_Sources/Solar_Panel/PanelTemp_C",
				BASE_PATH + "Energy_Sources/Solar_Panel/Efficiency_Percent"
			], [solar_power, solar_voltage, solar_current, irradiance, panel_temp, solar_eff])
			
			# DG Set
			dg_running = random.random() < 0.2  # 20% chance DG is on
			dg_power = rand(100, 800) if dg_running else 0
			dg_voltage = rand(380, 420)
			dg_current = round((dg_power * 1000) / dg_voltage, 2)
			fuel_level = rand(20, 100) if dg_running else rand(50, 100)
			rpm = random.randint(800, 1800) if dg_running else 0
			eng_temp = rand(60, 95) if dg_running else rand(30, 40)
			run_hours = system.tag.readBlocking([BASE_PATH + "Energy_Sources/DG_Set/RunHours"])[0].value
			if dg_running:
				run_hours += 1.0 / 3600
			system.tag.writeBlocking([
				BASE_PATH + "Energy_Sources/DG_Set/Power_kW",
				BASE_PATH + "Energy_Sources/DG_Set/Voltage_V",
				BASE_PATH + "Energy_Sources/DG_Set/Current_A",
				BASE_PATH + "Energy_Sources/DG_Set/Running_Status",
				BASE_PATH + "Energy_Sources/DG_Set/FuelLevel_Percent",
				BASE_PATH + "Energy_Sources/DG_Set/RunHours",
				BASE_PATH + "Energy_Sources/DG_Set/RPM",
				BASE_PATH + "Energy_Sources/DG_Set/EngineTemp_C"
			], [dg_power, dg_voltage, dg_current, dg_running, fuel_level, run_hours, rpm, eng_temp])
			
			# Main Line
			main_power = rand(1200, 1800) if solar_factor > 0.5 else rand(800, 1600)
			main_voltage = rand(415, 440)
			main_current = round((main_power * 1000) / main_voltage, 2)
			pf = rand(0.85, 0.98)
			freq = rand(49.8, 50.2)
			system.tag.writeBlocking([
				BASE_PATH + "Energy_Sources/Main_Line/Power_kW",
				BASE_PATH + "Energy_Sources/Main_Line/Voltage_V",
				BASE_PATH + "Energy_Sources/Main_Line/Current_A",
				BASE_PATH + "Energy_Sources/Main_Line/PowerFactor",
				BASE_PATH + "Energy_Sources/Main_Line/Frequency_Hz"
			], [main_power, main_voltage, main_current, pf, freq])
			
			# Totals
			grid_plus_solar = main_power + solar_power
			total_power = grid_plus_solar + dg_power
			system.tag.writeBlocking([
				BASE_PATH + "Energy_Sources/Grid_Plus_Solar_kW",
				BASE_PATH + "Energy_Sources/Total_Power_kW"
			], [grid_plus_solar, total_power])
			
			# Energy counters
			for path, val in {
				"Energy_Sources/Main_Line/Energy_kWh": main_power / 3600,
				"Energy_Sources/Solar_Panel/Energy_kWh": solar_power / 3600,
				"Energy_Sources/DG_Set/Energy_kWh": dg_power / 3600
			}.items():
				prev = system.tag.readBlocking([BASE_PATH + path])[0].value
				system.tag.writeBlocking([BASE_PATH + path], [prev + val])
		except Exception as e:
			logger.error("Error in simulate_energy_sources: " + str(e))
	
	# -----------------------------
	# Equipment Simulation (Krones, Packaging, Utilities)
	# -----------------------------
	def simulate_equipment():
		try:
			# Krones Ergobloc L
			running = random.random() < 0.8
			pwr = rand(200, 450) if running else rand(30, 60)
			speed = random.randint(400, 600) if running else 0
			bottles = system.tag.readBlocking([BASE_PATH + "Krones_Ergobloc_L/Bottles_Produced"])[0].value
			if running:
				bottles += int(speed / 60)
			eff = (speed / 600.0) * 100 if running else 0
			energy = system.tag.readBlocking([BASE_PATH + "Krones_Ergobloc_L/Energy_kWh"])[0].value + pwr / 3600
			energy_per_bottle = (energy * 1000 / bottles) if bottles > 0 else 0
			alarm = pwr > 500
			system.tag.writeBlocking([
				BASE_PATH + "Krones_Ergobloc_L/Running_Status",
				BASE_PATH + "Krones_Ergobloc_L/Power_kW",
				BASE_PATH + "Krones_Ergobloc_L/Production_Speed_BPM",
				BASE_PATH + "Krones_Ergobloc_L/Bottles_Produced",
				BASE_PATH + "Krones_Ergobloc_L/Efficiency_Percent",
				BASE_PATH + "Krones_Ergobloc_L/Energy_kWh",
				BASE_PATH + "Krones_Ergobloc_L/Energy_Per_Bottle_Wh",
				BASE_PATH + "Krones_Ergobloc_L/Alarm_Status"
			], [running, pwr, speed, bottles, eff, energy, energy_per_bottle, alarm])
			
			# Packaging Line
			pkg_running = random.random() < 0.85
			pkg_pwr = rand(100, 250) if pkg_running else rand(20, 40)
			speed_cpm = random.randint(15, 30) if pkg_running else 0
			cases = system.tag.readBlocking([BASE_PATH + "Packaging_Line/Cases_Packed"])[0].value
			if pkg_running:
				cases += speed_cpm / 60
			eff_pkg = (speed_cpm / 30.0) * 100 if pkg_running else 0
			energy_pkg = system.tag.readBlocking([BASE_PATH + "Packaging_Line/Energy_kWh"])[0].value + pkg_pwr / 3600
			system.tag.writeBlocking([
				BASE_PATH + "Packaging_Line/Running_Status",
				BASE_PATH + "Packaging_Line/Power_kW",
				BASE_PATH + "Packaging_Line/Speed_CPM",
				BASE_PATH + "Packaging_Line/Cases_Packed",
				BASE_PATH + "Packaging_Line/Efficiency_Percent",
				BASE_PATH + "Packaging_Line/Energy_kWh"
			], [pkg_running, pkg_pwr, speed_cpm, int(cases), eff_pkg, energy_pkg])
			
			# Compressor
			comp_run = random.random() < 0.7
			comp_pwr = rand(30, 60) if comp_run else rand(5, 10)
			pressure = rand(6, 9)
			eff = rand(80, 95)
			temp = rand(50, 80)
			system.tag.writeBlocking([
				BASE_PATH + "Utilities/Compressor/Running_Status",
				BASE_PATH + "Utilities/Compressor/Power_kW",
				BASE_PATH + "Utilities/Compressor/Pressure_Bar",
				BASE_PATH + "Utilities/Compressor/Efficiency_Percent",
				BASE_PATH + "Utilities/Compressor/Motor_Temperature_C"
			], [comp_run, comp_pwr, pressure, eff, temp])
	
			# Air Conditioning
			ac_run = random.random() < 0.8
			ac_power = rand(20, 60) if ac_run else rand(5, 10)
			ac_room_temp = rand(20, 26) if ac_run else rand(26, 30)
			ac_setpoint = 24.0
			ac_eff = 100 - abs(ac_room_temp - ac_setpoint) * 3
			ac_eff = max(min(ac_eff, 100), 70)
			ac_runtime = system.tag.readBlocking([BASE_PATH + "Utilities/Air_Conditioning/Compressor_Runtime_Hours"])[0].value
			ac_energy = system.tag.readBlocking([BASE_PATH + "Utilities/Air_Conditioning/Energy_kWh"])[0].value + ac_power / 3600
			if ac_run:
				ac_runtime += 1.0 / 3600
			system.tag.writeBlocking([
				BASE_PATH + "Utilities/Air_Conditioning/Running_Status",
				BASE_PATH + "Utilities/Air_Conditioning/Power_kW",
				BASE_PATH + "Utilities/Air_Conditioning/Room_Temperature_C",
				BASE_PATH + "Utilities/Air_Conditioning/SetPoint_C",
				BASE_PATH + "Utilities/Air_Conditioning/Efficiency_Percent",
				BASE_PATH + "Utilities/Air_Conditioning/Compressor_Runtime_Hours",
				BASE_PATH + "Utilities/Air_Conditioning/Energy_kWh"
			], [ac_run, ac_power, ac_room_temp, ac_setpoint, ac_eff, ac_runtime, ac_energy])
	
			# Refrigeration
			ref_run = random.random() < 0.9
			ref_power = rand(100, 300) if ref_run else rand(20, 50)
			ref_temp = rand(2, 8) if ref_run else rand(8, 15)
			ref_setpoint = 5.0
			ref_press = rand(3, 10)
			ref_eff = 100 - abs(ref_temp - ref_setpoint) * 5
			ref_eff = max(min(ref_eff, 95), 70)
			ref_defrost = random.random() < 0.1
			ref_energy = system.tag.readBlocking([BASE_PATH + "Utilities/Refrigeration/Energy_kWh"])[0].value + ref_power / 3600
			system.tag.writeBlocking([
				BASE_PATH + "Utilities/Refrigeration/Running_Status",
				BASE_PATH + "Utilities/Refrigeration/Power_kW",
				BASE_PATH + "Utilities/Refrigeration/Cold_Room_Temperature_C",
				BASE_PATH + "Utilities/Refrigeration/SetPoint_C",
				BASE_PATH + "Utilities/Refrigeration/Compressor_Pressure_Bar",
				BASE_PATH + "Utilities/Refrigeration/Efficiency_Percent",
				BASE_PATH + "Utilities/Refrigeration/Defrost_Cycle_Active",
				BASE_PATH + "Utilities/Refrigeration/Energy_kWh"
			], [ref_run, ref_power, ref_temp, ref_setpoint, ref_press, ref_eff, ref_defrost, ref_energy])
		except Exception as e:
			logger.error("Error in simulate_equipment: " + str(e))
	
	# -----------------------------
	# Shift Simulation
	# -----------------------------
	def simulate_shift_data():
		try:
			shift_path = BASE_PATH + "Shift_Data/"
			total_energy = system.tag.readBlocking([
				BASE_PATH + "Energy_Sources/Total_Power_kW"
			])[0].value
			
			current_time = system.date.now()
			hour = system.date.getHour24(current_time)
			
			# Shift logic (3 shifts of 8 hours)
			if 6 <= hour < 14:
				shift = 1
			elif 14 <= hour < 22:
				shift = 2
			else:
				shift = 3
			
			current_shift_tag = shift_path + "Current_Shift"
			prev_shift_tag = shift_path + "Previous_Shift_Energy_kWh"
			total_energy_tag = shift_path + "Shift_Total_Energy_kWh"
			target_tag = shift_path + "Shift_Target_Energy_kWh"
			start_time_tag = shift_path + "Shift_Start_Time"
	
			current_shift = system.tag.readBlocking([current_shift_tag])[0].value
			total_energy_val = system.tag.readBlocking([total_energy_tag])[0].value
			target_val = system.tag.readBlocking([target_tag])[0].value
	
			# If shift changes, reset shift values
			if shift != current_shift:
				system.tag.writeBlocking([
					current_shift_tag,
					prev_shift_tag,
					total_energy_tag,
					start_time_tag,
					target_tag
				], [
					shift,
					total_energy_val,  # last shift energy saved
					0.0,
					current_time,
					rand(1000, 2000)  # new target
				])
			else:
				# Increment total energy in shift
				new_total = total_energy_val + (total_energy / 3600)
				system.tag.writeBlocking([total_energy_tag], [new_total])
		except Exception as e:
			logger.error("Error in simulate_shift_data: " + str(e))
	
	# -----------------------------
	# Main Execution
	# -----------------------------
	try:
		simulate_energy_sources()
		simulate_equipment()
		simulate_shift_data()
	except Exception as e:
		logger.error("Main Simulation Error: " + str(e))