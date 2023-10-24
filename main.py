from gpxOnMaps import GpxOnMap
from access_token import token

if __name__ == '__main__':
    gpx_map = GpxOnMap()
    gpx_map.mapbox_access_token = token

    gpx_map.output_file_name = 'images/snohetta.jpg'
    gpx_map.mapbox_style = 'edriessen/clnymoa2t005101qx2du81zcr'
    gpx_map.plot_gpx_on_map(
        path_to_gpx='snohetta.gpx',
        route_title='SNØHETTA',
    )

    # sample 2
    gpx_map.output_file_name = 'images/ragocircuit.jpg'
    gpx_map.theme_primary_color = 'cornflowerblue'
    gpx_map.background_image_width = 900
    gpx_map.fig_size = (18, 12)
    gpx_map.plot_gpx_on_map(
        path_to_gpx='ragocircuit.gpx',
        route_title='THE RAGO CIRCUIT'
    )

    # sample 3
    gpx_map.output_file_name = 'images/tilburgtenmiles.jpg'
    gpx_map.theme_primary_color = 'darkorange'
    gpx_map.route_margin = .2
    gpx_map.plot_gpx_on_map(
        path_to_gpx='tilburgtenmiles.gpx',
        route_title='TILBURG TEN MILES',
    )
