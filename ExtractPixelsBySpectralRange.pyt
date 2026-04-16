import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Spectral Filter Toolbox"
        self.alias = "spectral"
        self.tools = [SpectralRangeTool]

class SpectralRangeTool(object):
    def __init__(self):
        self.label = "Extract Pixels By Spectral Range"
        self.description = (
            "Filters pixels from a multiband raster based on user-defined spectral intensity thresholds. "
            "Up to twenty bands can be filtered simultaneously, with each band assigned a minimum and maximum "
            "intensity value between 0 and 255. A pixel is only retained in the output if it satisfies the "
            "intensity range conditions for every selected band. Pixels that do not meet all conditions are "
            "set as NoData.\n\n"
            "Note: Additional band filter slots are revealed one at a time by checking the "
            "'Additional Band' checkbox at the bottom of each slot. Each new filter is applied "
            "on top of the previous ones, narrowing the selection further with each condition added."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Input Raster
        p0 = arcpy.Parameter(name="in_raster", displayName="Input Raster", 
                             datatype="GPRasterLayer", parameterType="Required", direction="Input")
        
        params = [p0]

        # Band selection 
        for i in range(1, 21):
            group = "Spectral Band Selection"
            
            # Band dropdown
            b = arcpy.Parameter(name=f"band_{i}", displayName=f"Select Band", 
                                datatype="GPString", parameterType="Optional", direction="Input")
            b.category = group
            
            # Min/Max nested underneath
            mi = arcpy.Parameter(name=f"min_{i}", displayName="Min Intensity", 
                                 datatype="GPLong", parameterType="Optional", direction="Input")
            mi.category = group
            mi.value = 0
            
            ma = arcpy.Parameter(name=f"max_{i}", displayName="Max Intensity", 
                                 datatype="GPLong", parameterType="Optional", direction="Input")
            ma.category = group
            ma.value = 255

            # The Checkbox
            add_more = arcpy.Parameter(name=f"add_{i}", displayName="Additional Band", 
                                       datatype="GPBoolean", parameterType="Optional", direction="Input")
            add_more.category = group
            add_more.value = False
            
            # Hide unused bands
            if i > 1:
                b.enabled = mi.enabled = ma.enabled = add_more.enabled = False
            
            params.extend([b, mi, ma, add_more])

        # Output Raster 
        p_out = arcpy.Parameter(name="out_raster", displayName="Output Raster", 
                                datatype="DERasterDataset", parameterType="Required", direction="Output")
        params.append(p_out)
        
        return params

    def updateParameters(self, parameters):
        # Populate band names
        if parameters[0].value:
            try:
                desc = arcpy.Describe(parameters[0].valueAsText)
                bands = [b.name for b in desc.children]
                # Update all 20 band dropdowns (indices 1, 5, 9, ... 77)
                for i in range(1, 81, 4): 
                    parameters[i].filter.list = bands
            except:
                pass

        # Reveal next slot only if the Additional Band checkbox is clicked
        for i in range(4, 77, 4): 
            if parameters[i].value == True:
                # Enable the next group of 4 parameters
                parameters[i+1].enabled = True 
                parameters[i+2].enabled = True 
                parameters[i+3].enabled = True 
                parameters[i+4].enabled = True 
            else:
                
                for j in range(i+1, 81):
                    parameters[j].enabled = False
                    if parameters[j].datatype == "GPBoolean":
                        parameters[j].value = False
        return

    def execute(self, parameters, messages):
        from arcpy.sa import Raster, SetNull, CreateConstantRaster
        import arcpy
        
        arcpy.CheckOutExtension("Spatial")

        in_ras_obj = parameters[0].value
        in_ras_path = in_ras_obj.dataSource if hasattr(in_ras_obj, 'dataSource') else parameters[0].valueAsText
        out_ras_path = parameters[-1].valueAsText
        
        arcpy.env.extent = in_ras_path
        arcpy.env.snapRaster = in_ras_path
        arcpy.env.cellSize = in_ras_path
        
        conditions = []
        
        for i in range(1, 81, 4):
            if parameters[i].valueAsText:
                band_name = parameters[i].valueAsText
                v_min = int(parameters[i+1].value)
                v_max = int(parameters[i+2].value)
                
                band_full_path = f"{in_ras_path}\\\\{band_name}"
                arcpy.AddMessage(f"Filtering {band_name}: {v_min}-{v_max}")
                
                band_ras = Raster(band_full_path)
                conditions.append((band_ras >= v_min) & (band_ras <= v_max))

        if conditions:
            final_mask = conditions[0]
            for cond in conditions[1:]:
                final_mask = final_mask & cond

            
            red_band = SetNull(final_mask == 0, CreateConstantRaster(255, "INTEGER", arcpy.env.cellSize, arcpy.env.extent))
            green_band = SetNull(final_mask == 0, CreateConstantRaster(0, "INTEGER", arcpy.env.cellSize, arcpy.env.extent))
            blue_band = SetNull(final_mask == 0, CreateConstantRaster(0, "INTEGER", arcpy.env.cellSize, arcpy.env.extent))

            arcpy.management.CompositeBands([red_band, green_band, blue_band], out_ras_path)
            arcpy.management.CalculateStatistics(out_ras_path)
            arcpy.SetParameterAsText(len(parameters)-1, out_ras_path)
        else:
            arcpy.AddError("No bands selected.")

        arcpy.CheckInExtension("Spatial")
