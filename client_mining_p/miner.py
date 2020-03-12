import hashlib
import json
import requests
import sys
import time


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True)
    seed = 0
    proof = f'I am Groot. {seed} 42'
    while valid_proof(block_string, proof) is False:
        seed += 1
        proof = f'I am Groot. {seed} 42'

    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:5] == '00000'


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # Run forever until interrupted
    coins = 0
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # Get the block from `data` and use it to look for a new proof
        print(f'Starting proof_of_work for block {data["index"]}.')
        start = time.time()
        new_proof = proof_of_work(data)
        end = time.time()
        print(f'Proof_of_work done for block {data["index"]}.')
        print(f'Proof completed in {end - start:.1f} seconds.')

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        # TODO handle non-json response
        mine_response = r.json()
        if mine_response['success']:
            coins += 1
            print(f'Mining for block {data["index"]} succeeded')
        else:
            print(f'Mining for block {data["index"]} did not succeed')

        # If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if mine_response['success']:
            print(f'Total number of coins is now {coins}')
        else:
            print(mine_response)
        print('')