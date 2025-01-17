import os
import csv
from datetime import datetime

class ExplorerTest:
    def __init__(self):
        # Test için algoritma ismini belirliyoruz
        self.algorithm = "astar"
        
        # Test için dosya adı oluşturuluyor
        self.csv_file = f"test_metrics_{self.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Dosyayı oluştur ve başlık satırını yaz
        self.create_csv_file()

    def create_csv_file(self):
        """
        CSV dosyasını oluşturur ve başlık satırını ekler.
        """
        with open(self.csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Algorithm', 'Goal_X', 'Goal_Y', 'Path_Length', 'Euclidean_Distance', 'Computation_Time', 'Memory_Usage_MB', 'Waypoint_Count'])
        print(f"CSV dosyası başarıyla oluşturuldu: {self.csv_file}")

    def write_metrics(self, goal_x, goal_y, path_length, euclidean_distance, computation_time, memory_usage, waypoint_count):
        """
        Metriği CSV dosyasına yazar.
        """
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.algorithm, goal_x, goal_y, path_length, euclidean_distance, computation_time, memory_usage, waypoint_count])
        print(f"Metriği CSV dosyasına yazıldı: {goal_x}, {goal_y}, {path_length}, {euclidean_distance}, {computation_time}, {memory_usage}, {waypoint_count}")

    def test_csv_file(self):
        """
        CSV dosyasını test eder.
        """
        # Örnek verilerle metrik yazma
        self.write_metrics(1.0, 2.0, 5.5, 2.2, 0.01, 50.5, 3)
        self.write_metrics(3.0, 4.0, 6.8, 3.7, 0.02, 52.3, 4)

        # Dosyanın oluşturulup oluşturulmadığını kontrol et
        if os.path.exists(self.csv_file):
            print(f"CSV dosyası mevcut: {self.csv_file}")
            
            # Dosya içeriğini okuyup yazdırma
            with open(self.csv_file, 'r') as file:
                content = file.readlines()
                print("Dosya içeriği:")
                for line in content:
                    print(line.strip())
        else:
            print("CSV dosyası oluşturulamadı!")

# Test sınıfını çalıştır
if __name__ == '__main__':
    explorer_test = ExplorerTest()
    explorer_test.test_csv_file()
