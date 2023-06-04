import yaml



if __name__ == '__main__':
    pass
    print("welcome use GPT doc translator")

    with open('translator.yaml', 'r',encoding="utf8") as f:
        options = yaml.safe_load(f)

    print(options)
