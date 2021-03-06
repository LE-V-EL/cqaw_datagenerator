from GeneratePreset import batch_generation

FULL_DATA_SIZE = 100000
MAX_BATCH_SIZE = 10000
generated_count = 0

p = './competition_data/'
batch_generation(path=p, prefix='', batch_idx=-1, batch_size=0) # Writes to the header of metadata

i = 0
while generated_count < FULL_DATA_SIZE: 
    batch_size = min(MAX_BATCH_SIZE, FULL_DATA_SIZE-generated_count)
    batch_generation(path=p, prefix='', batch_idx=i, batch_size=batch_size)
    generated_count = generated_count+batch_size
    i = i+1
