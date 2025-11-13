// Major ski resorts in North America with coordinates and elevation
const skiResorts = [
    {
        name: "Vail, CO",
        lat: 39.6403,
        lon: -106.3742,
        elevation: 2500,
        state: "Colorado"
    },
    {
        name: "Aspen Snowmass, CO",
        lat: 39.2091,
        lon: -106.9450,
        elevation: 2451,
        state: "Colorado"
    },
    {
        name: "Breckenridge, CO",
        lat: 39.4817,
        lon: -106.0384,
        elevation: 2926,
        state: "Colorado"
    },
    {
        name: "Park City, UT",
        lat: 40.6514,
        lon: -111.5079,
        elevation: 2103,
        state: "Utah"
    },
    {
        name: "Alta, UT",
        lat: 40.5885,
        lon: -111.6381,
        elevation: 2600,
        state: "Utah"
    },
    {
        name: "Jackson Hole, WY",
        lat: 43.5875,
        lon: -110.8281,
        elevation: 1924,
        state: "Wyoming"
    },
    {
        name: "Big Sky, MT",
        lat: 45.2846,
        lon: -111.4004,
        elevation: 2285,
        state: "Montana"
    },
    {
        name: "Whistler Blackcomb, BC",
        lat: 50.1163,
        lon: -122.9574,
        elevation: 2182,
        state: "British Columbia"
    },
    {
        name: "Lake Tahoe - Squaw Valley, CA",
        lat: 39.1970,
        lon: -120.2356,
        elevation: 1890,
        state: "California"
    },
    {
        name: "Mammoth Mountain, CA",
        lat: 37.6308,
        lon: -119.0326,
        elevation: 2424,
        state: "California"
    },
    {
        name: "Steamboat, CO",
        lat: 40.4583,
        lon: -106.8048,
        elevation: 2103,
        state: "Colorado"
    },
    {
        name: "Telluride, CO",
        lat: 37.9375,
        lon: -107.8123,
        elevation: 2659,
        state: "Colorado"
    },
    {
        name: "Sun Valley, ID",
        lat: 43.6963,
        lon: -114.3575,
        elevation: 2788,
        state: "Idaho"
    },
    {
        name: "Killington, VT",
        lat: 43.6046,
        lon: -72.8220,
        elevation: 1293,
        state: "Vermont"
    },
    {
        name: "Stowe, VT",
        lat: 44.5303,
        lon: -72.7817,
        elevation: 1165,
        state: "Vermont"
    },
    {
        name: "Sunday River, ME",
        lat: 44.4696,
        lon: -70.8565,
        elevation: 870,
        state: "Maine"
    },
    {
        name: "Mt. Bachelor, OR",
        lat: 43.9792,
        lon: -121.6889,
        elevation: 2764,
        state: "Oregon"
    },
    {
        name: "Crystal Mountain, WA",
        lat: 46.9356,
        lon: -121.4744,
        elevation: 2286,
        state: "Washington"
    },
    {
        name: "Taos, NM",
        lat: 36.5928,
        lon: -105.4464,
        elevation: 2804,
        state: "New Mexico"
    },
    {
        name: "Heavenly, CA/NV",
        lat: 38.9352,
        lon: -119.9394,
        elevation: 3068,
        state: "California/Nevada"
    }
];

// Sort resorts alphabetically by name
skiResorts.sort((a, b) => a.name.localeCompare(b.name));
