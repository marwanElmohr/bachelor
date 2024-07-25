import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import xmlrpc.client
import time
from datetime import datetime
from temp import arroyo  
from pypylon import pylon
import lasercontrol
import mcs
import smaract.ctl as ctl

class CameraApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera App")
        self.root.geometry("1000x800") 
        self.style = ttk.Style()
        self.style.configure("SystemPanel.TFrame", background="gray")
        self.IdDocLive = None
        
        self.system_panel, self.canvas = self.create_system_panel("pylon", (1, 0, 1))
        self.system_panel.grid(row=0, column=0, sticky="nsew") 
        
        self.system_panel2, self.canvas2 = self.create_system_panel("TECsource-LaserSource", (1, 0, 1))
        self.system_panel2.grid(row=0, column=1) 
        
        self.system_panel3, self.canvas3 = self.create_system_panel("Beam Controller", (1, 0, 1))
        self.system_panel3.grid(row=1, column=0) 
        
        self.system_panel4, self.canvas4 = self.create_system_panel("SmarAct MCS2", (1, 0, 1))
        self.system_panel4.grid(row=1, column=1, sticky="nsew") 
        
        
        ttk.Label(self.system_panel4, text="Enter X Value:").grid(row=1, column=0, padx=5, pady=(0, 100))
        self.x_value_entry = ttk.Entry(self.system_panel4)
        self.x_value_entry.grid(row=1, column=1, padx=5, pady=(0, 100))
        
        ttk.Label(self.system_panel4, text="Enter Y Value:").grid(row=1, column=0, padx=5, pady=(10, 5))
        self.y_value_entry = ttk.Entry(self.system_panel4)
        self.y_value_entry.grid(row=1, column=1, padx=5, pady=(10, 5))
        
        ttk.Label(self.system_panel4, text="Enter Z Value:").grid(row=1, column=0, padx=5, pady=(100, 5))
        self.z_value_entry = ttk.Entry(self.system_panel4)
        self.z_value_entry.grid(row=1, column=1, padx=5, pady=(100, 5))
        
        self.set_values_button = ttk.Button(self.system_panel4, text="Set Values", command=self.set_mcs_values)
        self.set_values_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.set_values_button = ttk.Button(self.system_panel4, text="Read Values", command=self.read_mcs_values)
        self.set_values_button.grid(row=4, column=1, columnspan=2, pady=10)
    
    
        self.root.columnconfigure(0, weight=1, minsize=0)  
        self.root.columnconfigure(1, weight=1, minsize=400)  
        self.root.rowconfigure(0, weight=2)  
        self.root.rowconfigure(1, weight=1)  
        
        
        self.proxy = xmlrpc.client.ServerProxy("http://172.20.10.6:8080/")  # Adjusted IP address
        
        
        #beam profiler
        self.select_camera_button = tk.Button(self.system_panel3, text="Select Camera", command=self.select_camera)
        self.select_camera_button.grid(row=1, column=0, padx=0, pady=(10, 140))  


        self.wavelength_label = ttk.Entry(self.system_panel3)
        self.wavelength_label.grid(row=1, column=1, padx=5, pady=(10, 120)) 
        ttk.Label(self.system_panel3, text="Enter Wavelength (nm):").grid(row=1, column=1, padx=10, pady=(10, 170))
        
        

        self.calibration_button = tk.Button(self.system_panel3, text="Perform Background Calibration", command=self.background_calibration)
        self.calibration_button.grid(row=1, column=0, padx=5, pady=(190,180))  

        self.serial_entry = ttk.Entry(self.system_panel3)
        self.serial_entry.grid(row=1, column=1, padx=5, pady=(50,0)) 
        ttk.Label(self.system_panel3,text="Enter Laser Serial Number:").grid(row=1, column=1,padx=5,pady=(0,0))

        self.measure_button = tk.Button(self.system_panel3, text="Perform Measurement", command=self.perform_measurement)
        self.measure_button.grid(row=1, column=0, padx=5, pady=(160,0))  

        self.remeasure_button = tk.Button(self.system_panel3, text="Re-measure", command=self.remeasure)
        self.remeasure_button.grid(row=1, column=1, padx=5, pady=(160, 0)) 

#basler
        self.camera = None
        self.initialize_camera()

        self.root.bind('<Escape>', self.exit_app)

        self.video_capture_in_progress = False
        
        self.stop_recording_button = ttk.Button(self.system_panel, text="Stop Recording", command=self.stop_recording)
        self.stop_recording_button.grid(row=0, column=1, sticky="ew")  # Place the stop recording button in row 0, column 1
        
        self.start_recording_button = ttk.Button(self.system_panel, text="Start Recording", command=self.start_recording)
        self.start_recording_button.grid(row=0, column=1, sticky="ew")  # Place the start recording button in row 0, column 0
        
        self.start_button = ttk.Button(self.system_panel, text="Single Shot", command=self.capture_media)
        self.start_button.grid(row=0, column=2, sticky="ew")  # Place the start button in row 0, column 2
#arroyo
        self.controller = lasercontrol.laser1()
        
        self.temperature_entry = ttk.Entry(self.system_panel2)
        self.temperature_entry.grid(row=1, column=0,  padx=(70,10), pady=(10, 0)) 
        ttk.Label(self.system_panel2, text="Desired Temperature (°C)").grid(row=1, column=0, padx=(70,10), pady=(10, 70)) 
        self.current_entry = ttk.Entry(self.system_panel2)
        self.current_entry.grid(row=1, column=1,  padx=(10,10), pady=(10, 0))  
        self.read_current_button = ttk.Button(self.system_panel2, text="Read Current", command=self.read_current)
        self.read_current_button.grid(row=2, column=2, padx=5, pady=10)
        ttk.Label(self.system_panel2, text="Desired Current (Amps)").grid(row=1, column=1, padx=5, pady=(10, 70))  

        ttk.Button(self.system_panel2, text="Set Temperature", command=self.set_temperature).grid(row=2, column=0,  padx=(10,50), pady=0)  
        ttk.Button(self.system_panel2, text="Set Current", command=self.set_current).grid(row=2, column=1,  padx=(10,80), pady=10)  
#live feed function and basler
        self.mcs_handle = mcs.initialize_and_return_handle()
    def create_system_panel(self, system_name, bg_color):
        system_panel = ttk.Frame(self.root, style="SystemPanel.TFrame")
        system_panel.configure(style="SystemPanel.TFrame")

        name_label = ttk.Label(system_panel, text=system_name)
        name_label.grid(row=0, column=0, columnspan=3, sticky="nw", padx=5, pady=0)


        canvas = tk.Canvas(system_panel, width=440, height=290,background ="gray") 
        canvas.grid(row=1, column=0, columnspan=3, padx=8, pady=5)

        return system_panel, canvas

    def initialize_camera(self):
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        except pylon.RuntimeException:
            messagebox.showerror("Camera Error", "Failed to initialize camera. Please make sure the camera is connected.")
            self.camera = None

    def start_live_feed(self):
        try:
            if self.camera is not None and not self.camera.IsGrabbing():
                self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                while True:
                    grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    if grabResult and grabResult.GrabSucceeded():
                        image = grabResult.GetArray()
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                        image = Image.fromarray(image)
                        image = image.resize((640, 480), Image.LANCZOS)  # Use LANCZOS for resizing

                        image = ImageTk.PhotoImage(image=image)
                        self.canvas.create_image(0, 0, anchor="nw", image=image)
                        self.canvas.image = image 
                    grabResult.Release()
                    self.root.update() 
                    if self.video_capture_in_progress:
                        break  
        except KeyboardInterrupt:
            pass  
        finally:
            if self.camera is not None:
                self.camera.StopGrabbing()

    def capture_photo(self, output_dir):
        try:
            if self.camera is not None and not self.camera.IsGrabbing():
                self.camera.Open()
                grabResult = self.camera.GrabOne(5000)
                if grabResult and grabResult.GrabSucceeded():
                    image = grabResult.GetArray()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(output_dir, f"photo_{timestamp}.jpg")
                    cv2.imwrite(filename, image)

                    messagebox.showinfo("Photo Taken", f"The photo has been captured and saved as '{filename}'.")

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
                    image = Image.fromarray(image)
                    image = image.resize((640, 480), Image.LANCZOS)  
                    image = ImageTk.PhotoImage(image=image)
                    self.canvas.create_image(0, 0, anchor="nw", image=image)
                    self.canvas.image = image  

                    # Stop the live feed
                    self.camera.StopGrabbing()
        except pylon.RuntimeException as e:
            print("Failed to capture image:", e)
        finally:
            if self.camera is not None:
                self.camera.Close()

    def capture_video(self, output_dir):
        try:
            if self.camera is not None:
                output_file = os.path.join(output_dir, "captured_video.avi")
                if self.camera.IsGrabbing():
                    messagebox.showerror("Error", "Grabbing is already in progress.")
                    return

                self.video_capture_in_progress = True
                out = None  
# camera settings
                camera = self.camera
                try:
                    camera.Open()
                    camera.AutoFunctionProfile.Value = "MinimizeGain"
                    
                    camera.AutoFunctionProfile.Value = "MinimizeExposureTime"
                    
                    camera.GainAuto.Value = "Continuous"
                    camera.ExposureAuto.Value = "Continuous"
                    
                    camera.ExposureAuto.SetValue("Off")
                    camera.ExposureTime.SetValue(10000.0) 

                    camera.GainAuto.SetValue("Off")
                    camera.Gain.SetValue(0.0) 
                    
                    camera.PixelFormat.SetValue("BGR8")
                    
                    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                    
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    frame_rate = 7.5  
                    out = cv2.VideoWriter(output_file, fourcc, frame_rate, (camera.Width.GetValue(), camera.Height.GetValue()))

                    while camera.IsGrabbing() and self.video_capture_in_progress:
                        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                        if grabResult.GrabSucceeded():
                            
                            img = grabResult.Array
                            
                          
                            out.write(img)
                            
                            
                            cv2.imshow("Live Video", img)

                            
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

                        grabResult.Release()
                except KeyboardInterrupt:
                    print("Video capture terminated by user.")
                except pylon.RuntimeException as e:
                    print("Failed to capture video:", e)
                finally:
                    if out is not None:
                        out.release()
                    if camera is not None:
                        camera.StopGrabbing()
                    cv2.destroyAllWindows()
        except Exception as e:
            print("Error capturing video:", e)
            messagebox.showerror("Error", "Failed to capture video.")

    def start_recording(self):
        output_dir = filedialog.askdirectory()  
        if output_dir:
            if self.camera is not None:
                self.camera.StopGrabbing()
            self.capture_video(output_dir)
            self.start_recording_button.grid_remove()
            self.stop_recording_button.grid()

    def stop_recording(self):
        self.video_capture_in_progress = False
        self.stop_recording_button.grid_remove()
        self.start_recording_button.grid()

    def exit_app(self, event=None):  
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        os._exit(0)

    def run(self):
        self.start_live_feed()
        self.root.mainloop()

    def capture_media(self, event=None):
        option = "Photo"  
        if option == "Photo": 
            output_dir = filedialog.askdirectory() 
            if output_dir:
                self.capture_photo(output_dir)
        elif option == "Video":  
            self.start_recording()
#arroyo functions
    def set_temperature(self):
        desired_temperature = float(self.temperature_entry.get())
        controller.set_temp(desired_temperature)

    def set_current(self):
        try:
            desired_current = float(self.current_entry.get())
            # Call the set_current method from the lasercontrol module
            self.controller.set_current(desired_current)  # Using self.controller instance
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric value for the current.")
    def read_current(self):
        try:
            current = self.controller.read_current()
            messagebox.showinfo("Current Reading", f"Current set point: {current}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read current: {str(e)}")

#beam functions
    def select_camera(self):
        try:
            if self.IdDocLive is None:
                self.IdDocLive, self.CameraItem, self.OpenedLiveMode = self.selectCamera()
                messagebox.showinfo("Camera Selected", f"Using camera {self.CameraItem['sName']}")
                self.start_beam_recording()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_beam_recording(self):
        try:
            videoDocId = self.proxy.RayCi.LiveMode.Measurement.newVideo(self.IdDocLive)
            self.proxy.RayCi.Video.Recording.Settings.setCodec(videoDocId, "LAGS")
            self.proxy.RayCi.Video.Recording.Settings.setFreeRunning(videoDocId)
            self.proxy.RayCi.Video.Recording.start(videoDocId)

            print("Recording video for 20 seconds...")
            time.sleep(20) 
            print("Recording video for 20 seconds...done")
            self.proxy.RayCi.Video.Recording.stop(videoDocId)
            save_path = "D:\captured\MyRecordedVideo.avi"
            self.proxy.RayCi.Video.saveAs(videoDocId, save_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def background_calibration(self):
        try:
            if self.IdDocLive:
                self.backgroundCalibration(self.IdDocLive)
                messagebox.showinfo("Calibration Done", "Background calibration completed successfully!")
            else:
                messagebox.showwarning("Warning", "Please select a camera first.")
        except Exception as e:
                messagebox.showerror("Error", str(e))
    def perform_measurement(self):
        try:
            if self.IdDocLive:
                laser_sno = self.serial_entry.get()  
                IdDocSingle = self.performMeasurement(self.IdDocLive, laser_sno)  
                messagebox.showinfo("Measurement Done", "Measurement completed successfully!")
                self.evaluate_measurement(IdDocSingle)
            else:
                messagebox.showwarning("Warning", "Please select a camera first.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def performMeasurement(self, IdDocLive, LaserSNo):
        self.proxy.RayCi.LiveMode.AOI.Adjustment.setActive(IdDocLive, True)
        # open a new single measurement
        IdDocSingle = self.proxy.RayCi.LiveMode.Measurement.newSingle(IdDocLive)
        # configure single measurement
        self.proxy.RayCi.Single.Header.Laser.setSerial(IdDocSingle, str(LaserSNo))
        # configure measurement process, average over 8 frames
        self.proxy.RayCi.Single.Recording.Settings.setSingleShot(IdDocSingle, False)
        self.proxy.RayCi.Single.Recording.Settings.setFrameSpan(IdDocSingle, 8)
        self.proxy.RayCi.Single.Recording.Settings.setMedian(IdDocSingle, True)
        # start measurement
        self.proxy.RayCi.Single.Recording.start(IdDocSingle)
        # wait until measurement is finished
        print('Measurement started, please wait', end='', flush=True)
        time.sleep(0.1)
        while self.proxy.RayCi.Single.Recording.isRecording(IdDocSingle):
            print('.', sep='', end='', flush=True)
            time.sleep(0.2)
        print()
        print('Finished measurement')
        return IdDocSingle


    def remeasure(self):
        self.wavelength_entry.delete(0, tk.END)
        self.serial_entry.delete(0, tk.END)

    def selectCamera(self):
        IdDocLive = None
        CameraItem = None
        OpenedLiveMode = False

        # get list of all opened Live Modes
        LiveModeList = self.proxy.RayCi.LiveMode.list()

        # search for the first camera already connected to a Live Mode
        for LiveModeItem in LiveModeList:
            if LiveModeItem['sName'] != 'not connected':
                ConsideredTempCamera = self.proxy.RayCi.LiveMode.Camera.getIdCurrentCam(LiveModeItem['nIdDoc'])
                if ConsideredTempCamera['sName'] != 'Video Stream':  # Live Mode must be connected to a real camera
                    IdDocLive = LiveModeItem['nIdDoc']
                    CameraItem = ConsideredTempCamera
                    OpenedLiveMode = False  # don't close it after usage
                    break

        if IdDocLive is None:  # if no running camera, that is already connected to a Live Mode, was found
            # get number of connected cameras
            CameraCount = self.proxy.RayCi.LiveMode.Camera.getIdCamListSize()
            if CameraCount == 0:
                raise Exception('No camera found.')
            # open new Live Mode with the first available camera
            CameraItem = self.proxy.RayCi.LiveMode.Camera.getIdCamListItem(-1, 0)
            IdDocLive = self.proxy.RayCi.LiveMode.open(CameraItem['nIdCamHigh'], CameraItem['nIdCamLow'])
            print('Opened new Live Mode')
            OpenedLiveMode = True  # close after usage
        print('Using camera', CameraItem['sName'])
        print(self.proxy.RayCi.LiveMode.isConnected)

        return IdDocLive, CameraItem, OpenedLiveMode

    def backgroundCalibration(self, IdDocLive):
        # configure background calibration, average over 16 frames
        self.proxy.RayCi.LiveMode.Background.Recording.Settings.setFrameSpan(IdDocLive, 16)
        self.proxy.RayCi.LiveMode.Background.Recording.Settings.setAllExposure(IdDocLive)
        # start calibration
        self.proxy.RayCi.LiveMode.Background.Recording.start(IdDocLive)
        # wait until calibration is done
        print('Background calibration started, please wait', end='', flush=True)
        time.sleep(0.1)
        while self.proxy.RayCi.LiveMode.Background.Recording.isRecording(IdDocLive):
            print('.', sep='', end='', flush=True)
            time.sleep(0.2)
        print()
        print('Finished background calibration')
        
    def evaluateFWHM(self, IdDocSingle, IdCrossSect):
        # adjust to the center of the beam, if possible
        self.proxy.RayCi.Single.CrossSection.adjust(IdDocSingle, IdCrossSect, 1)
        # configure the first cursor pair for FWHM = 50%
        self.proxy.RayCi.Single.CrossSection.Cursor.Settings.setBeamWidthRatio(IdDocSingle, IdCrossSect, 0, 50.0)
        # read distance
        return self.proxy.RayCi.Single.CrossSection.Cursor.getDistance(IdDocSingle, IdCrossSect, 0)

    def evaluateFWHM_xy(self, IdDocSingle):
        IdCrossSectX = 0
        IdCrossSectY = 1
        SizeX = self.proxy.RayCi.Single.Data.getSizeX()
        SizeY = self.proxy.RayCi.Single.Data.getSizeY()
        # open cross-section through the center of the image
        self.proxy.RayCi.Single.CrossSection.Settings.setX_px(IdDocSingle, IdCrossSectX, int(SizeY / 2))
        self.proxy.RayCi.Single.CrossSection.Settings.setY_px(IdDocSingle, IdCrossSectY, int(SizeX / 2))
        # evaluate FWHM
        FWHM_x = self.evaluateFWHM(IdDocSingle, IdCrossSectX)
        FWHM_y = self.evaluateFWHM(IdDocSingle, IdCrossSectY)
        Unit = self.proxy.RayCi.Single.CrossSection.Cursor.getUnit(IdDocSingle, IdCrossSectY)
        return (FWHM_x, FWHM_y, Unit)

    def evaluate2ndMoments_xy(self, IdDocSingle):
        Center_x = self.proxy.RayCi.Single.Analysis.SecondMoments.Centroid.getX(IdDocSingle)
        Center_y = self.proxy.RayCi.Single.Analysis.SecondMoments.Centroid.getY(IdDocSingle)
        Width_x = self.proxy.RayCi.Single.Analysis.SecondMoments.WidthLab.getX(IdDocSingle)
        Width_y = self.proxy.RayCi.Single.Analysis.SecondMoments.WidthLab.getY(IdDocSingle)
        Unit = self.proxy.RayCi.Single.Analysis.SecondMoments.WidthLab.getUnit(IdDocSingle)
        return (Center_x, Center_y, Width_x, Width_y, Unit)

    def saveMeasurement(self, IdDocSingle, PathName):
        base_file, ext = os.path.splitext(PathName)
        self.proxy.RayCi.Single.saveAs(IdDocSingle, base_file + '.tif', True)
        self.proxy.RayCi.Single.Data.exportAsCsv(IdDocSingle, base_file + '.csv', ',', True)

    def evaluate_measurement(self, IdDocSingle):
        try:
            Center_x, Center_y, Width_x, Width_y, Width_Unit = self.evaluate2ndMoments_xy(IdDocSingle)
            print("\n2nd Moments:")
            print("Center x: ", Center_x, Width_Unit)
            print("Center y: ", Center_y, Width_Unit)
            print("Width  x: ", Width_x, Width_Unit)
            print("Width  y: ", Width_y, Width_Unit)

            FWHM_x, FWHM_y, FWHM_Unit = self.evaluateFWHM_xy(IdDocSingle)
            print("\nFWHM   x: ", FWHM_x, FWHM_Unit)
            print("FWHM   y: ", FWHM_y, FWHM_Unit)

        except Exception as e:
            print("Error during evaluation:", e)
            
    def set_mcs_values(self):
        x_value = self.x_value_entry.get()
        y_value = self.y_value_entry.get()
        z_value = self.z_value_entry.get()

        # Convert values to float if they are not empty
        if x_value != "":
            x_value = float(x_value)
        else:
            x_value = None

        if y_value != "":
            y_value = float(y_value)
        else:
            y_value = None

        if z_value != "":
            z_value = float(z_value)
        else:
            z_value = None

        # Set values using move_axis if they are not None
        if x_value is not None:
            mcs.move_axis(self.mcs_handle, 'X', x_value)
        if y_value is not None:
            mcs.move_axis(self.mcs_handle, 'Y', y_value)
        if z_value is not None:
            mcs.move_axis(self.mcs_handle, 'Z', z_value)

        messagebox.showinfo("Set Values", "Values set successfully.")
       
    def read_mcs_values(self):
        try:
            # Read current positions from the MCS device
            mcs.read_positions(self.mcs_handle)
            
            # Fetch the latest positions from the MCS device
            x_position = ctl.GetProperty_i64(self.mcs_handle, 0, ctl.Property.POSITION) / 1000000  # Convert picometers to microns
            y_position = ctl.GetProperty_i64(self.mcs_handle, 1, ctl.Property.POSITION) / 1000000  # Convert picometers to microns
            z_position = ctl.GetProperty_i64(self.mcs_handle, 2, ctl.Property.POSITION) / 1000000  # Convert picometers to microns

            # Show positions in a message box
            messagebox.showinfo("Current Values", f"X: {x_position} microns, Y: {y_position} microns, Z: {z_position} microns")
        except Exception as e:
            # Show error message if an exception occurs
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = CameraApp()
    controller = arroyo()

    app.run()
