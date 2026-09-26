import calculator
import utils

def run():
    val = calculator.run_calculation()
    print(utils.format_output(val))
    avg = calculator.calculate_average([10, 20, 30])
    print(utils.format_avg(avg))

if __name__ == "__main__":
    run()
