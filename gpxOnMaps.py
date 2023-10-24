import gpxpy
import numpy as np
import requests
import matplotlib.pyplot as plt

class GpxOnMap:

    def __init__(self):
        self.mapbox_access_token = ''
        self.fig_size = (12,14)

        self.background_image_width = 600
        self.background_image_height = 700
        self.route_margin = .1
        self.background_image_name = 'plot_background.jpg'
        self.output_file_name = 'gpx_on_map.jpg'

        self.mapbox_style = 'mapbox/light-v11'
        self.theme_primary_color = '#F14F54'
        self.theme_secondary_color = '#444444'

        self.x_values = []
        self.y_values = []

        self.long_min = 0
        self.long_max = 0
        self.lat_min = 0
        self.lat_max = 0

    def load_gpx(self, path_to_gpx):
        gpx_file = open(path_to_gpx, 'r')

        gpx = gpxpy.parse(gpx_file)

        self.x_values = []
        self.y_values = []

        gpx_tracks = gpx.tracks

        for gpx_track in gpx_tracks:
            gpx_segments = gpx_track.segments
            for gpx_segment in gpx_segments:

                gpx_points = gpx_segment.points

                for gpx_point in gpx_points:
                    self.x_values.append(gpx_point.longitude)
                    self.y_values.append(gpx_point.latitude)

    def set_geo_min_max(self):
        self.long_min = min(self.x_values)
        self.long_max = max(self.x_values)
        self.lat_min = min(self.y_values)
        self.lat_max = max(self.y_values)

    def add_geo_margin(self):
        long_range = self.long_max - self.long_min
        self.long_min -= long_range * self.route_margin
        self.long_max += long_range * self.route_margin

        lat_range = self.lat_max - self.lat_min
        self.lat_max -= lat_range * self.route_margin
        self.lat_max += lat_range * self.route_margin

    def haversine(self, lon1, lat1, lon2, lat2, earth_radius=6367):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)

        source = https://stackoverflow.com/questions/53697724/getting-distance-from-longitude-and-latitude-using-haversines-distance-formula
        """
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(
            dlon / 2.0) ** 2

        c = 2 * np.arcsin(np.sqrt(a))
        km = earth_radius * c
        return km
    def correct_geo_bbox(self):
        map_aspect = self.background_image_width/self.background_image_height

        geo_w = self.long_max - self.long_min
        geo_h = self.lat_max - self.lat_min

        harv_w = self.haversine(
            self.long_min, self.lat_min,
            self.long_max, self.lat_min
        )
        harv_h = self.haversine(
            self.long_min, self.lat_min,
            self.long_min, self.lat_max
        )

        harv_aspect = harv_w/harv_h

        if harv_aspect > map_aspect:
            lat_h = geo_h * (harv_aspect / map_aspect)
            lat_middle = (geo_h / 2) + self.lat_min

            self.lat_min = lat_middle - (lat_h / 2)
            self.lat_max = lat_middle + (lat_h / 2)

        elif harv_aspect < map_aspect:
            long_w = geo_w * (harv_aspect / map_aspect)
            long_middle = geo_w / 2 + self.long_min

            self.long_min = long_middle - (long_w / 2)
            self.long_max = long_middle + (long_w / 2)

    def get_mapbox_static_image(self):
        """
        # https://docs.mapbox.com/playground/static/
        :return:
        """
        bbox = (
            f'['
                f'{str(self.long_min)},'
                f'{str(self.lat_min)},'
                f'{str(self.long_max)},'
                f'{str(self.lat_max)}'
            f']'
        )

        reso = f'{str(self.background_image_width)}x{str(self.background_image_height)}'

        link = (
            f'https://api.mapbox.com/styles/v1'
            f'/{self.mapbox_style}'
            f'/static/{bbox}'
            f'/{reso}@2x'
            f'?logo=false'
            f'&padding=0'
            f'&access_token={self.mapbox_access_token}'
            f'&attribution=false'
        )

        result = requests.get(link, allow_redirects=False)
        if result.status_code == 200:
            with open(self.background_image_name, 'wb') as f:
                f.write(result.content)
                f.close()
        else:
            print(f'Error getting Mapbox Static Image, code {result.status_code}.')

    def plot_route(self, route_title):
        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.plot(
            self.x_values,
            self.y_values,
            color=self.theme_primary_color,
            lw=2,
            zorder=1
        )
        ax.axis('off')

        img_url = self.background_image_name
        img = plt.imread(img_url)
        ax.imshow(
            img,
            extent=[self.long_min, self.long_max, self.lat_min, self.lat_max],
            aspect='auto'
        )

        ax.set_xlim([self.long_min, self.long_max])
        ax.set_ylim([self.lat_min, self.lat_max])

        long_center = ((self.long_max - self.long_min) / 2) + self.long_min

        ax.text(
            x=long_center,
            y=self.lat_min + ((self.lat_max - self.lat_min) * .1),
            s=route_title,
            ha='center',
            fontsize=44,
            fontfamily='Roboto',
            fontweight='black',
            color=self.theme_primary_color
        )

        ax.text(
            x=long_center,
            y=self.lat_min + ((self.lat_max - self.lat_min) * .05),
            s='map data by © Mapbox and © OpenStreetMap',
            ha='center',
            fontsize=12,
            fontfamily='Roboto',
            fontweight='normal',
            color=self.theme_secondary_color
        )

        plt.savefig(self.output_file_name, bbox_inches='tight')

    def plot_gpx_on_map(self, path_to_gpx, route_title):
        self.load_gpx(path_to_gpx=path_to_gpx)
        self.set_geo_min_max()
        self.add_geo_margin()
        self.correct_geo_bbox()
        self.get_mapbox_static_image()
        self.plot_route(route_title)



