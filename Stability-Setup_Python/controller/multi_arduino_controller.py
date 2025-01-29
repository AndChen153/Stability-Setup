# multi_arduino_controller.py
from controller.single_arduino_controller import single_controller
from controller import arduino_assignment
from constants import Mode, constants_controller
from data_visualization import data_plotter
from datetime import datetime
import threading
import os
from helper.global_helpers import custom_print


class multi_controller:
    def __init__(self,
                 trial_name: str,
                 date: str,
                 plot_location="",
                 plotting_mode=False):
        self.trial_name = ""
        if trial_name:
            self.trial_name = trial_name + " "
        self.folder_path = "./data/" + trial_name + date + "/"
        self.date = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.arduino_assignments = None
        self.controllers = {}
        self.active_threads = {}
        self.lock = threading.Lock()
        self.plotting_mode = plotting_mode
        self.plot_location = plot_location

        # Initialize controllers
        if not self.plotting_mode:
            self.arduino_assignments = arduino_assignment.get()

            if not os.path.exists(self.folder_path):
                os.mkdir(self.folder_path)

            for arduino in self.arduino_assignments:
                ID = arduino["ID"]
                COM = arduino["com"]

                controller = single_controller(
                    arduinoID=ID,
                    COM=COM,
                    SERIAL_BAUD_RATE=constants_controller["serial_baud_rate"],
                    trial_name=self.trial_name,
                    date=self.date,
                    folder_path=self.folder_path,
                )
                self.controllers[ID] = controller

                if controller.connect():
                    custom_print(f"Connected to {controller.port}.")
                else:
                    custom_print(f"Connection to {controller.port} failed.")

    def get_valid(self):
        return bool(self.arduino_assignments) or self.plotting_mode

    def run_command(self, ID, command, **kwargs):
        """
        Runs a command on a specific controller. If another command is already running,
        it stops the current command before starting the new one.
        """
        custom_print(f"Attempting to run {command} on controller {ID}")
        custom_print(self.active_threads)
        with self.lock:
            # Stop existing commands if running
            if ID in self.active_threads:
                custom_print(f"Stopping current command on controller {ID}.")
                self.controllers[ID].reset_arduino()
                thread = self.active_threads[ID]
                thread.join()
                del self.active_threads[ID]

            # Define the target function based on the command
            if command == Mode.SCAN:
                target = lambda: self.controllers[ID].scan(**kwargs)
            elif command == Mode.PNO:
                target = lambda: self.controllers[ID].pno(**kwargs)
            elif command == Mode.CONSTANT:
                target = lambda: self.controllers[ID].constant_voltage(**kwargs)
            elif not (command == Mode.STOP):
                custom_print(f"Unknown command: {command}")
                return

            if not (command == Mode.STOP):
                # Start the new command in a new thread
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                self.active_threads[ID] = thread
                custom_print(f"Started command {command} on controller {ID}.")

    def run(self, mode, params=[]):
        """
        Runs a specified mode on all connected controllers.
        """
        if mode == Mode.PLOTTER:
            data_plotter.plot_all_in_folder(self.plot_location)
        else:
            kwargs = {
                "params": params,
            }
            for controller_id in self.controllers:
                try:
                    self.run_command(controller_id, mode, **kwargs)
                except Exception as e:
                    custom_print(
                        f"Failed to run command '{mode}' on controller {controller_id}: {e}"
                    )