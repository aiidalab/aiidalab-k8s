import hiyapyco

with open('./jupyterhub/values.yaml.orig') as fp:
    values = fp.read()
with open('./config.yaml') as fp:
    config = fp.read()

merged_yaml = hiyapyco.load([values, config], method=hiyapyco.METHOD_MERGE)
print(hiyapyco.dump(merged_yaml))
