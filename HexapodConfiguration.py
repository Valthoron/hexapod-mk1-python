import xml.etree.ElementTree as ElementTree

azimuth_angles = [-45, 0, 45]
azimuth_pulses = [1800, 1325, 850]
hip_angles = [-47, 0, 55]
hip_pulses = [1900, 1415, 860]
knee_angles = [-118, -90, 0]
knee_pulses = [820, 1100, 2000]

biases = [0] * 9

def load_configuration():
    global azimuth_angles
    global azimuth_pulses
    global hip_angles
    global hip_pulses
    global knee_angles
    global knee_pulses
    global biases

    # Parse configuration XML
    configuration_xml = ElementTree.parse("Configuration.xml")
    configuration = configuration_xml.getroot()

    # Parse angle-pulse tables
    azimuth_table = configuration.find("ServoCalibration/AzimuthTable")
    hip_table = configuration.find("ServoCalibration/HipTable")
    knee_table = configuration.find("ServoCalibration/KneeTable")

    azimuth_angles, azimuth_pulses = parse_table(azimuth_table)
    hip_angles, hip_pulses = parse_table(hip_table)
    knee_angles, knee_pulses = parse_table(knee_table)

    # Parse pulse biases
    bias_tables = [\
    configuration.find("ServoCalibration/Bias/Leg1"), \
    configuration.find("ServoCalibration/Bias/Leg2"), \
    configuration.find("ServoCalibration/Bias/Leg3"), \
    configuration.find("ServoCalibration/Bias/Leg4"), \
    configuration.find("ServoCalibration/Bias/Leg5"), \
    configuration.find("ServoCalibration/Bias/Leg6"), \
    ]

    biases = []

    for leg_table in bias_tables:
        biases.extend([\
            float(leg_table.attrib["Azimuth"]), \
            float(leg_table.attrib["Hip"]), \
            float(leg_table.attrib["Knee"]), \
            ])

def parse_table(table):
    breakpoints = []
    values = []
    have_value = False

    for line in table.text.splitlines():
        line = line.strip()

        # Skip if line is empty or only whitespace
        if not line:
            continue

        # Split into words and get rid of whitespace
        words = line.split()

        # Need at least 2 values (extra values are ignored)
        if len(words) < 2:
            continue

        breakpoints.append(float(words[0]))
        values.append(float(words[1]))
        have_value = True

    if have_value:
        return breakpoints, values
    else:
        return [0.0], [0.0]
