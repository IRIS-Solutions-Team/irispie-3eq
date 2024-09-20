
import irispie as ir

m_json = ir.Simultaneous.from_json_file("model.json", )
m_json.solve()

m_pickle = ir.Simultaneous.from_pickle_file("model_2.pkl", )

m_pickle_2 = ir.load_pickle("model_2.pkl", )

