# multi_arduino_controller.py
import threading
import os
import time
import json
from controller.email_service import EmailSender
from datetime import datetime

from controller.single_arduino_controller import SingleController
from controller import arduino_assignment
from constants import Mode, Constants
from data_visualization import data_plotter
from helper.global_helpers import logger
from PySide6.QtCore import QObject, Signal, Slot, Qt

class MultiController(QObject):
    started = Signal()
    finished = Signal()
    def __init__(self):
        super().__init__()

    def initializeMeasurement(
        self,
        trial_name: str,
        data_dir: str,
        email: str,
        email_user: str,
        email_pass: str,
        date: str,
        json_location,
        plot_location="",
        plotting_mode=False,
    ):
        if trial_name != "":
            self.trial_name = "__" + trial_name
        else:
            self.trial_name = ""
        self.trial_dir = os.path.join(data_dir, f"{date}{self.trial_name}")

        self.trial_date = None
        self.arduino_ids = self.load_arduino_ids(json_location)
        self.assigned_connected_arduinos = []
        self.connected_arduinos_HWID = []
        self.controllers = {}
        self.active_threads = {}
        self.lock = threading.Lock()
        self.plotting_mode = plotting_mode
        self.plot_location = plot_location

        self.email = email
        self.email_sender = EmailSender(email_user, email_pass)
        self.mode = None

        self.unknownID = []
        unique_Arduino_ID = True

        # Initialize controllers
        threads = []

        # Define a worker function for each thread.
        def init_controller(ID, COM):
            nonlocal unique_Arduino_ID

            self.arduino_ids = self.load_arduino_ids(json_location)
            controller = SingleController(
                COM=COM,
                trial_name=self.trial_name,
                trial_dir=self.trial_dir,
                arduino_ids=self.arduino_ids,
            )
            connected_result = controller.connect()
            if connected_result:
                HW_ID, Arduino_ID = connected_result
                Arduino_ID = int(Arduino_ID)
                # Ensure thread-safe modifications to shared variables.
                with self.lock:
                    self.connected_arduinos_HWID.append(HW_ID)
                    if Arduino_ID in self.controllers:
                        unique_Arduino_ID = False
                    elif (Arduino_ID is not None) and Arduino_ID == -1:
                        self.unknownID.append(HW_ID)
                    elif (Arduino_ID is not None) and Arduino_ID > -1:
                        logger.log(f"Connected to {controller.port}.")
                        self.assigned_connected_arduinos.append((HW_ID, Arduino_ID))
                        self.controllers[Arduino_ID] = controller
                    else:
                        logger.log(f"Connection to {controller.port} failed.")
            else:
                return False

        # Start a thread for each COM port in the assignment.
        for ID, COM in enumerate(arduino_assignment.get()):
            logger.log(f"Trying to connect to {COM}")
            thread = threading.Thread(target=init_controller, args=(ID, COM))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish.
        for thread in threads:
            thread.join()

        if self.unknownID or not unique_Arduino_ID:
            return False
        else:
            return True

    def reset_arduinos(self):
        for ID in self.controllers:
            self.controllers[ID].disconnect()
            self.controllers[ID].connect()
            #TODO: thread


    def get_valid(self):
        return bool(self.assigned_connected_arduinos) or self.plotting_mode

    def run(self, mode, params=dict[str, str]):
        """
        Runs a specified mode on all connected controllers.
        """
        if not os.path.exists(self.trial_dir):
            os.mkdir(self.trial_dir)
        self.mode = mode

        kwargs = {
            "params": params,
        }
        for controller_id in self.controllers:
            try:
                self.run_command(controller_id, mode, **kwargs)
            except Exception as e:
                logger.log(
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
        logger.log(f"Attempting to run {command} on controller {ID}")
        # logger.log(self.active_threads)
        with self.lock:
            # Stop existing commands if running
            if ID in self.active_threads:
                logger.log(f"Stopping current command on controller {ID}.")
                self.controllers[ID].should_run = False
                self.controllers[ID].reset_arduino()
                thread = self.active_threads[ID]
                thread.join()
                del self.active_threads[ID]

            # Define the target function based on the command
            # TODO: put date here
            if command == Mode.SCAN:
                target = lambda: self.controllers[ID].scan(**kwargs)
            elif command == Mode.MPPT:
                target = lambda: self.controllers[ID].mppt(**kwargs)
            elif command == Mode.STOP:
                logger.log(f"STOPPING SINGLE CONTROLLER {ID}")
            elif not (command == Mode.STOP):
                logger.log(f"Unknown command: {command}")
                return

            if not (command == Mode.STOP):
                # Start the new command in a new thread
                logger.log(f"Started command {command} on controller {ID}.")
                self.controllers[ID].date = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                self.active_threads[ID] = thread

    def monitor_controllers(self):
        self.started.emit()
        while True:
            with self.lock:
                finished_ids = [
                    ID for ID, thread in self.active_threads.items()
                    if not thread.is_alive()
                ]
                for ID in finished_ids:
                    del self.active_threads[ID]
                if not self.active_threads:
                    break
            time.sleep(0.1)
        self.finished.emit()
        if self.email:
            self.email_sender.send_email(
                subject="Stability Setup Notification - Test Finished",
                body=f"{self.mode} named: {self.trial_name[2:]} started at {self.trial_date} has finished.",
                to_email=self.email,
            )

    def load_arduino_ids(self, json_location):
        """Load JSON data from the specified file and extract the 'arduino_ids' section."""
        try:
            with open(json_location, "r") as f:
                full_data = json.load(f)
            return full_data.get("arduino_ids", {})
        except Exception as e:
            logger.log(f"Error loading JSON: {e}")
            return {}

