from flask import Flask, request, jsonify

app = Flask(__name__)

def is_prime(n):
    """A simple function to check if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

@app.route('/calculate', methods=['POST'])
def calculate_primes():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')

    if start is None or end is None:
        return jsonify({"error": "Please provide 'start' and 'end' values."}), 400

    primes = [num for num in range(start, end + 1) if is_prime(num)]

    return jsonify({
        "range": f"{start}-{end}",
        "prime_count": len(primes),
        "primes": primes
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)