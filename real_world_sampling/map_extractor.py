from pykml import parser
from lxml import etree
import logging as log
import glob
import os
from operator import itemgetter


def extract_coordinates(map_size: int) -> list:
    # Define the path to the directory containing KML files
    path = 'real_world_sampling/kml-files'

    # Initialize an empty list to store coordinates from all KML files
    list_of_coords = []

    for filename in glob.glob(os.path.join(path, '*.kml')):
        # Parse the KML file
        doc = parser.parse(filename)

        # Convert the parsed KML document to a string
        doc_string = etree.tostring(doc)

        # Parse the string to an XML tree structure
        root = parser.fromstring(doc_string)

        # Extract the coordinates element from the KML structure
        coordinates = root.Document.Placemark.LineString.coordinates
        coord_string = etree.tostring(coordinates).decode("utf-8")

        # Split the coordinate string into a list, removing the first two and last elements
        coord_list = coord_string.split()[2:-1]

        coords = []
        for line in coord_list:
            # Split the coordinate string by ',' and remove the last element (altitude)
            str_list = line.split(',')[:-1]

            # Convert the coordinate strings to float and create a tuple
            coord_tuple = list(map(float, str_list))

            # Convert the latitude and longitude to a more manageable format
            coord_tuple[0] = str(abs(int(coord_tuple[0] * 10000000)))
            coord_tuple[1] = str(abs(int(coord_tuple[1] * 10000000)))

            # Append the processed coordinates to the list
            coords.append(coord_tuple)

        # Normalize the coordinates based on common prefixes and minimum values
        # This is useful for aligning the coordinates to a common reference point
        x_coords, y_coords = [i[0] for i in coords], [i[1] for i in coords]
        same_x, same_y = os.path.commonprefix(x_coords), os.path.commonprefix(y_coords)

        # Adjust the coordinates based on the common prefixes and minimum values
        for i in range(len(x_coords)):
            l = list(coords[i])
            l[0] = l[0][len(same_x):]
            l[0] = float(l[0][:1] + "." + l[0][1:])
            l[1] = l[1][len(same_y):]
            l[1] = float(l[1][:1] + "." + l[1][1:])
            coords[i] = tuple(l)

        # Calculate the minimum x and y values to normalize the coordinates
        min_x, min_y = min(coords, key=itemgetter(0))[0], min(coords, key=itemgetter(1))[1]

        # Adjust the coordinates to start from (0,0) based on the minimum values
        for i in range(len(x_coords)):
            l = list(coords[i])
            l[0] = l[0] - int(min_x)
            l[1] = l[1] - int(min_y)
            coords[i] = tuple(l)

        # Determine the scaling factor based on the maximum coordinate value and map size
        max_x, max_y = max(coords, key=itemgetter(0))[0], max(coords, key=itemgetter(1))[1]
        max_value = max(max_x, max_y)
        multi = int((map_size - 20) / max_value)

        # Scale the coordinates to fit within the specified map size
        for i in range(len(coords)):
            j = list(coords[i])
            j[0] = int(j[0] * multi)
            j[1] = int(j[1] * multi)
            coords[i] = tuple(j)

        # Append the processed coordinates for the current KML file to the list
        list_of_coords.append(coords)

    # Return the list containing coordinates from all processed KML files
    return list_of_coords

def main() -> int:
    """Printing the coordinates for the real-wold maps"""
    coordinates_list = extract_coordinates(map_size=1000)
    print(len(coordinates_list))
    for i in range(len(coordinates_list)):
        print(coordinates_list[i])

    return 0

if __name__ == '__main__':
    main()
