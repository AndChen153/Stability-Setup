# multi_arduino_controller.py
import threading
import os
import time
from controller.email_service import EmailSender
from datetime import datetime

from controller.single_arduino_controller import SingleController
from controller import arduino_assignment
from constants import Mode, Constants
from data_visualization import data_plotter
from helper.global_helpers import custom_print

class MultiController:
    def __init__(self):
        self.email_sender = EmailSender()

    def initializeMeasurement(
        self,
        trial_name: str,
        data_dir: str,
        email: str,
        date: str,
        plot_location="",
        plotting_mode=False,
    ):
        if trial_name != "":
            self.trial_name = "__" + trial_name
        else:
            self.trial_name = ""
        self.trial_dir = os.path.join(data_dir, f"{date}{self.trial_name}")

        custom_print(self.trial_dir)

        self.trial_date = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
        self.arduino_assignments = None
        self.controllers = {}
        self.active_threads = {}
        self.lock = threading.Lock()
        self.plotting_mode = plotting_mode
        self.plot_location = plot_location

        self.email = email
        self.mode = None

        # Initialize controllers
        if not self.plotting_mode:
            self.arduino_assignments = arduino_assignment.get()

            if not os.path.exists(self.trial_dir):
                os.mkdir(self.trial_dir)

            for ID, COM in enumerate(self.arduino_assignments):
                controller = SingleController(
                    COM=COM,
                    SERIAL_BAUD_RATE=Constants.serial_baud_rate,
                    trial_name=self.trial_name,
                    date=self.trial_date,
                    trial_dir=self.trial_dir,
                )
                self.controllers[ID] = controller

                if controller.connect():
                    custom_print(f"Connected to {controller.port}.")
                else:
                    custom_print(f"Connection to {controller.port} failed.")

    def get_valid(self):
        return bool(self.arduino_assignments) or self.plotting_mode

    def run(self, mode, params=[]):
        """
        Runs a specified mode on all connected controllers.
        """
        self.mode = mode
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

            monitor_thread = threading.Thread(
                target=self.monitor_controllers, daemon=True
            )
            monitor_thread.start()

    def run_command(self, ID, command, **kwargs):
        """
        Runs a command on a specific controller. If another command is already running,
        it stops the current command before starting the new one.
        """
        custom_print(f"Attempting to run {command} on controller {ID}")
        # custom_print(self.active_threads)
        with self.lock:
            # Stop existing commands if running
            if ID in self.active_threads:
                custom_print(f"Stopping current command on controller {ID}.")
                self.controllers[ID].should_run = False
                self.controllers[ID].reset_arduino()
                thread = self.active_threads[ID]
                thread.join()
                del self.active_threads[ID]

            # Define the target function based on the command
            if command == Mode.SCAN:
                target = lambda: self.controllers[ID].scan(**kwargs)
            elif command == Mode.MPPT:
                target = lambda: self.controllers[ID].mppt("", **kwargs)
            elif command == Mode.STOP:
                custom_print("STOPPING SINGLE CONTROLLER")
                del self.controllers[ID]
            elif not (command == Mode.STOP):
                custom_print(f"Unknown command: {command}")
                return

            if not (command == Mode.STOP):
                # Start the new command in a new thread
                custom_print(f"Started command {command} on controller {ID}.")
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                self.active_threads[ID] = thread


    def monitor_controllers(self):
        while True:
            with self.lock:
                # Remove any threads that have finished
                finished_ids = [
                    ID
                    for ID, thread in self.active_threads.items()
                    if not thread.is_alive()
                ]
                for ID in finished_ids:
                    del self.active_threads[ID]

                if not self.active_threads:
                    break

            time.sleep(0.1)
        if self.email:
            self.email_sender.send_email(
                subject="Stability Setup Notification - Test Finished",
                body=f"{self.mode} named: {self.trial_name} started at {self.trial_date} has finished.",
                to_email=self.email,
            )
