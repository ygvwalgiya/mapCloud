import numpy as np

# Taken from trcsourcestep/trcdata.py
# Reads data from trc file into dict

class TRCData(dict):
    def load(self, filename):
        header_read_successfully = False
        labels = []
        with open(filename) as f:
            contents = f.readlines()
            line_count = 0
            for line in contents:
                line_count += 1
                line = line.strip()
                if line_count == 1:
                    # File Header 1
                    sections = line.split('\t')
                    self[sections[0]] = sections[1]
                    self['DataFormat'] = sections[2]
                    data_format_count = len(sections[2].split('/'))
                    self['FileName'] = sections[3]
                elif line_count == 2:
                    # File Header 2
                    file_header_keys = line.split('\t')
                elif line_count == 3:
                    # File Header 3
                    file_header_data = line.split('\t')
                    if len(file_header_keys) == len(file_header_data):
                        for index, key in enumerate(file_header_keys):
                            if key == 'Units':
                                self[key] = file_header_data[index]
                            else:
                                self[key] = float(file_header_data[index])
                    else:
                        raise IOError('File format invalid: File header keys count (%d) is not equal to file header data count (%d)' % (len(file_header_keys), len(file_header_data)))
                elif line_count == 4:
                    # Data Header 1
                    data_header_labels = line.split('\t')
                    if data_header_labels[0] != 'Frame#':
                        raise IOError('File format not valid data header does not start with "Frame#".')
                    if data_header_labels[1] != 'Time':
                        raise IOError('File format not valid data header in position 2 is not "Time".')

                    self['Frame#'] = []
                    self['Time'] = []
                elif line_count == 5:
                    # Data Header 1
                    data_header_sublabels = line.split('\t')
                    if len(data_header_labels) != len(data_header_sublabels):
                        raise IOError('File format invalid: Data header labels count (%d) is not equal to data header sub-labels count (%d)' % (len(data_header_labels), len(data_header_sublabels)))

                    labels = []
                    for label in data_header_labels:
                        label = label.strip()
                        if len(label):
                            self[label] = []
                            labels.append(label)

                    self['Labels'] = labels
                elif line_count == 6 and len(line) == 0:
                    # Blank line
                    header_read_successfully = True
                else:
                    # Some files don't have a blank line at line six
                    if line_count == 6:
                        header_read_successfully = True
                    # Data section
                    if header_read_successfully:
                        sections = line.split('\t')

                        frame = int(sections.pop(0))
                        self['Frame#'].append(frame)

                        time = float(sections.pop(0))
                        self['Time'].append(time)

                        len_section = len(sections)
                        if len_section % data_format_count == 0:
                            data = [[float(sections[subindex]) for subindex in range(index, index + data_format_count)] for index in range(0, len_section, data_format_count)]
                            self[frame] = (time, data)

                            for index, label_data in enumerate(data):
                                # Add two to the index as we want to skip 'Frame#' and 'Time'
                                self[labels[index + 2]] += [label_data]

                        else:
                            raise IOError('File format invalid: data frame %d does not match the data format' % len_section)


trcdata = TRCData()
# pretty self explanatory, this is hard coded rn
trcdata.load("Static_H23s1.trc")


# Taken from trcframeselectorstep/step.py/execute(self)
# returns landmark positions at specified frame
# currently hard coded
frame = 3

landmarksNames = trcdata['Labels']
try:
    time, landmarksCoords = trcdata[frame]
except KeyError:
    print('Frame {} not found'.format(frame))
    raise KeyError
            
landmarksNamesData = [frame, time] + landmarksCoords
landmarks = dict(zip(landmarksNames, landmarksNamesData))
if 'Frame#' in landmarks:
    del landmarks['Frame#']
if 'Time' in landmarks:
    del landmarks['Time']

for k, v in landmarks.items():
    landmarks[k] = np.array(v)

# The landmarkss will somehow have to be matched up to the landmarks listed here
DEFAULT_MODEL_LANDMARKS = (
    'pelvis-LASIS', 'pelvis-RASIS', 'pelvis-Sacral',
    'femur-MEC-l', 'femur-LEC-l', 
    'femur-MEC-r', 'femur-LEC-r',
    'tibiafibula-MM-l', 'tibiafibula-LM-l',
    'tibiafibula-MM-r', 'tibiafibula-LM-r',
    )
print(DEFAULT_MODEL_LANDMARKS)


# Taken from FieldworkLowerLimb2SideGenerationStep/step.py
'''
Outputs
    -------
    fieldworkmodeldict : dict
        A dictionary of customised fieldwork models of lower limb bones.
        Dictionary keys are: "pelvis", "pelvis flat", 'hemipelvis-left",
        "hemipelvis-right", "sacrum", "femur-l", "femur-r", "tibiafibula-l",
        "tibiafibula-r", "tibia-l", "tibia-r", "fibula-l", 'fibula-r",
        "patella-l", "patella-r".
    LowerLimbAtlas : LowerLimbAtlas instance
'''

config = {}
config['identifier'] = ''
config['GUI'] = 'False'
config['registration_mode'] = 'shapemodel'
config['pcs_to_fit'] = '1'
config['mweight'] = '0.1'
config['knee_corr'] = 'False'
config['knee_dof'] = 'False'
config['marker_radius'] = '5.0'
config['skin_pad'] = '5.0'
config['landmarks'] = {}
config['data_dir'] = 'workflow_plugins/fieldworklowerlimb2sidegenerationstep/'
for l in DEFAULT_MODEL_LANDMARKS:
            config['landmarks'][l] = ''

# Boilerplate code to match the required landmarks in config with the correct imported landmarks
# will need to get the user to input this one eventually
config['landmarks']['pelvis-LASIS'] = 'LASI'
config['landmarks']['pelvis-RASIS'] = 'RASI'
config['landmarks']['pelvis-Sacral'] = 'Sacral'
config['landmarks']['femur-MEC-l'] = 'LMFC'
config['landmarks']['femur-LEC-l'] = 'LLFC'
config['landmarks']['femur-MEC-r'] = 'RMFC'
config['landmarks']['femur-LEC-r'] = 'RLFC'
config['landmarks']['tibiafibula-MM-l'] = 'LTB4'
config['landmarks']['tibiafibula-LM-l'] = 'LTB2'
config['landmarks']['tibiafibula-MM-r'] = 'RTB4'
config['landmarks']['tibiafibula-LM-r'] = 'RTB2'

# An EDITED version of llstep
import llstep_jason as llstep

data = llstep.LLStepData(config)

data.inputLandmarks = landmarks
data.loadData()
data.updateFromConfig()
print('LL estimation configs:')
print(data.config)
data.register()

print('outputting {}'.format(data.outputModelDict.keys()))
outputModel = data.outputModelDict

lowerlimbatlas = data.LL

# Taken from FieldworkGait2392GeomStep
'''
Inputs
    ------
    gias-lowerlimb : gias2.musculoskeletal.bonemodel.LowerLimbAtlas instance
        Lower limb model to be used to customise gait2392.
    fieldworkmodeldict : dict [optional]
        Bone models to be used to customisation gait2392.
        Dictionary keys should be:
            pelvis
            femur-l
            femur-r
            patella-l
            patella-r
            tibiafibula-l
            tibiafibula-r
    
    Outputs
    -------
    opensimmodel : opensim.model instance
        The customised gait2392 opensim model
    gias-lowerlimb : gias2.musculoskeletal.bonemodel.LowerLimbAtlas instance
        The lowerlimb model used in the customisation
'''

