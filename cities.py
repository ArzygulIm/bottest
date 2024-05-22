import json
import os


class City:
    def __init__(self, name, attractions, map_data, hotels):
        self.name = name
        self.attractions = attractions
        self.map_data = map_data
        self.hotels = hotels

    def to_dict(self):
        return {
            'name': self.name,
            'attractions': self.attractions,
            'map_data': self.map_data,
            'hotels': self.hotels
        }


class CityDatabase:
    def __init__(self, filename='cities.json'):
        self.filename = filename
        self.cities = self.load_cities()

    def load_cities(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_cities(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.cities, file, ensure_ascii=False, indent=4)

    def add_city(self, city):
        self.cities.append(city.to_dict())
        self.save_cities()


# Example usage:
if __name__ == "__main__":
    city_name = input('Введите название города: ')
    attr_list = []
    while True:
        attraction = input('Введите имя достопримечательности: ')
        if attraction == '':
            break
        attraction_info = input("Введите информацию об этом месте: ")
        lat = float(input('Введите lat: '))
        lon = float(input('Введите lon: '))
        attr_list.append({"name": attraction, "attraction_info": attraction_info, 'map_data': {'lat': lat, 'lon': lon}})

    map_data = {"lat": float(input("Введите lat: ")), "lon": float(input("Введите lon: "))}

    hotels_list = []
    while True:
        hotel = input('Введите имя отеля: ')
        if hotel == '':
            break
        hotel_info = input("Введите информацию об этом месте: ")
        prices_from = int(input("Введите нач цену: "))
        sales = input("Введите скидки, акции: ")
        lat = float(input('Введите lat: '))
        lon = float(input('Введите lon: '))
        hotels_list.append({"name": hotel, "hotel_info": attraction_info, 'prices_from': prices_from, 'sales': sales,
                            'map_data': {'lat': lat, 'lon': lon}})

    city = City(city_name, attr_list, map_data, hotels_list)

    db = CityDatabase()
    db.add_city(city)
    print("City added successfully.")
