import util

# Generates the data.h file
def generateDataHeader(data):
    headers = ""
    out = ""
    # Generate initializers
    for field in data.iter("struct"):
        if "init" not in field.attrib:
            continue
        out += "int " + field.attrib["init"] + "(void);\n"

    out += "\n"
    # Generate data structures
    for struct in data.iter("struct"):
        if "comment" in struct.attrib:
            out += util.generateComment(struct.attrib["comment"], 100)
        out += "typedef struct " + struct.attrib["id"] + "_t {\n"

        # Semaphores
        out += "\tpthread_mutex_t " + struct.attrib["id"] + "Mutex;\n"

        for field in struct:
            if "comment" in field.attrib:
                out += util.generateComment(field.attrib["comment"], 100, "\t")
            fieldId = (
                "*"
                if ("pointer" in field.attrib and field.attrib["pointer"] == "true")
                else ""
            ) + field.attrib["id"]
            if field.tag == "struct":
                out += "\tstruct " + field.attrib["id"] + "_t " + fieldId + ";\n"
            elif field.tag == "field":
                fieldType = field.attrib["type"]
                # Deal with arrays
                if field.attrib["type"].endswith("]"):
                    fieldId += "[" + field.attrib["type"].split("[")[1]
                    fieldType = field.attrib["type"].split("[")[0]
                out += "\t" + fieldType + " " + fieldId + ";\n"

                # Create getter and setter headers
                # headers += util.generateComment("Getter and setter for " + struct.attrib["id"] + "->" + field.attrib["id"], 100)
                fieldType = field.attrib["type"]
                isArray = False
                if "[" in field.attrib["type"]:
                    fieldType = fieldType.split("[")[0]
                    isArray = True
                # headers += fieldType + " get" + util.capitalize(struct.attrib["id"]) + util.capitalize(field.attrib["id"]) + "();\n"
                # headers += "void set" + util.capitalize(struct.attrib["id"]) + util.capitalize(field.attrib["id"]) + "(" + fieldType + " val);\n\n"

                headers += (
                    fieldType
                    + " "
                    + util.getGetReference(struct, field)
                    + "("
                    + ("int index" if isArray else "")
                    + ");\n"
                )
                headers += (
                    "void "
                    + util.getSetReference(struct, field)
                    + "("
                    + fieldType
                    + " val"
                    + (", int index" if isArray else "")
                    + ");\n\n"
                )
        out += "} " + struct.attrib["id"] + "_t;\n\n"
    return out + "\n" + headers + "\n\n\n"


def generateInitC(data):

    defaultValues = {"bool": "false", "int": "0", "float": "0.0f", "double": "0.0"}

    out = ""

    # initMetaData()
    out += "int initMetaData() {\n"
    for struct in data.iter("struct"):
        out += (
            "\tif(("
            + util.getDataReference(struct, data)
            + " = ("
            + struct.attrib["id"]
            + "_t"
            + "*) malloc(sizeof("
            + struct.attrib["id"]
            + "_t"
            + "))) == NULL) { return 1; }\n"
        )
    out += "\n\treturn 0;"
    out += "\n}\n\n"

    for struct in data.iter("struct"):
        if "init" in struct.attrib:
            out += "int " + struct.attrib["init"] + "() { \n"

            # Generate the initData()
            if struct.attrib["id"] == "data":
                # Runs all of the initializers
                out += util.generateComment("Initializes all data points", 100, "\t")

                # Init meta data
                out += "\tif (initMetaData() != 0) {\n"
                out += '\t\tfprintf(stderr, "Failed to init meta data\\n");\n'
                out += "\t\treturn -1;\n"
                out += "\t}\n"

                for structuresToBeInitialized in data.iter("struct"):
                    if "init" in structuresToBeInitialized.attrib:
                        if structuresToBeInitialized.attrib["id"] != "data":
                            out += (
                                "\tif ("
                                + structuresToBeInitialized.attrib["init"]
                                + "() != 0) {\n"
                            )
                            out += (
                                '\t\tfprintf(stderr, "Failed to init '
                                + structuresToBeInitialized.attrib["id"]
                                + ' data\\n");\n'
                            )
                            out += "\t\treturn -1;\n"
                            out += "\t}\n"
                out += "\n"

            # Initialize mutexes
            out += util.generateComment("Initialize mutex", indentation="\t")
            out += (
                "\tif(pthread_mutex_init(&"
                + util.getMutexReference(struct, data)
                + ", NULL) != 0) {\n"
            )
            out += "\t\treturn 1;\n"
            out += "\t}\n\n"

            for field in struct:
                if field.tag == "field":

                    # Initialize the values

                    arrayLength = -1

                    if "[" in field.attrib["type"]:
                        fieldType = field.attrib["type"].split("[")[0]
                        arrayLength = field.attrib["type"].split("[")[1].split("]")[0]
                    else:
                        fieldType = field.attrib["type"]

                    # Deal with arrays
                    if arrayLength != -1:
                        out += "\tfor(int i = 0; i < " + arrayLength + "; i++)\n"
                        out += "\t\t" + util.getSetReference(struct, field) + "("

                    # Non-arrays
                    else:
                        out += "\t" + util.getSetReference(struct, field) + "("

                    # Figure out what to set as the default value
                    if fieldType in defaultValues:
                        out += defaultValues[fieldType]
                    elif "int" in fieldType:
                        out += defaultValues["int"]
                    else:
                        print(
                            "WARNING: AUTO-CODER COULD NOT FIND DEFAULT VALUE FOR TYPE '"
                            + fieldType
                            + "'."
                        )
                        out += "0"

                    if arrayLength != -1:
                        out += ", i"

                    out += ");\n"

            out += "\treturn 0;"
            out += "\n}\n\n"
    return out


def generateDataC(data):
    out = ""
    for struct in data.iter("struct"):
        for field in struct:
            if field.tag == "field":
                fieldType = field.attrib["type"]
                isArray = False

                # Deal with arrays
                if "[" in fieldType:
                    fieldType = fieldType.split("[")[0]
                    isArray = True

                # Getter
                out += (
                    fieldType
                    + " "
                    + util.getGetReference(struct, field)
                    + "("
                    + ("int index" if isArray else "")
                    + ") {\n"
                )
                out += (
                    "\tpthread_mutex_lock(&"
                    + util.getMutexReference(struct, data)
                    + ");\n"
                )
                out += (
                    "\t"
                    + fieldType
                    + " val = "
                    + util.getDataReference(field, data)
                    + ("[index]" if isArray else "")
                    + ";\n"
                )
                out += (
                    "\tpthread_mutex_unlock(&"
                    + util.getMutexReference(struct, data)
                    + ");\n"
                )
                out += "\treturn val;"
                out += "\n}\n\n"

                # Setter
                out += (
                    "void "
                    + util.getSetReference(struct, field)
                    + "("
                    + fieldType
                    + " val"
                    + (", int index" if isArray else "")
                    + ") {\n"
                )
                out += (
                    "\tpthread_mutex_lock(&"
                    + util.getMutexReference(struct, data)
                    + ");\n"
                )
                out += (
                    "\t"
                    + util.getDataReference(field, data)
                    + ("[index]" if isArray else "")
                    + "  = val;\n"
                )
                out += (
                    "\tpthread_mutex_unlock(&"
                    + util.getMutexReference(struct, data)
                    + ");"
                )
                out += "\n}\n\n"
    return out


# Generates the code which includes all of the data.h fields in TelemetryLoop.cpp
def generateBufferContents(data):
    out = ""
    for struct in data.iter("struct"):
        for field in struct:
            if field.tag == "field":

                # Deal with arrays

                arrayLength = -1

                if "[" in field.attrib["type"]:
                    fieldType = field.attrib["type"].split("[")[0]
                    arrayLength = field.attrib["type"].split("[")[1].split("]")[0]
                else:
                    fieldType = field.attrib["type"]

                # Deal with arrays
                if arrayLength != -1:
                    out += "for(int i = 0; i < " + arrayLength + "; i++)\n"
                    out += (
                        "\taddToBuffer(&buffer, "
                        + util.getGetReference(struct, field)
                        + "(i));\n"
                    )

                # Other cases
                else:
                    out += (
                        "addToBuffer(&buffer, "
                        + util.getGetReference(struct, field)
                        + "());\n"
                    )
    return out
