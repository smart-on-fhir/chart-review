import unittest
from chart_review import common
from chart_review import config
from chart_review import external
from chart_review.cohort import CohortReader

test_project_dir = '/opt/labelstudio/suicide-icd10/jan22-without-history'

class TestLabelstudio2Sql(unittest.TestCase):

    def map_ids_chart_to_fhir(self) -> dict:
        """
        Supports encounter_ref only
        :return:  dict[chart_id, fhir_id]
        """
        mappings = dict()

        exported_json = common.read_json(f"{test_project_dir}/labelstudio-export.json")
        for row in exported_json:
            chart_id = row['id']    # fail fast
            encounter_ref = row.get("data", {}).get("anon_id", None)
            mappings[chart_id] = {'encounter_ref':  encounter_ref, 'mentions': dict()}
        return mappings

    def merge_ids_and_mentions(self) -> dict:
        """
        merge chart:fhir indentifiers with the map of mentions
        """
        mappings = self.map_ids_chart_to_fhir()
        reader = CohortReader(config.ProjectConfig(test_project_dir))

        for annotator in reader.annotations.mentions:
            mentions = reader.annotations.mentions[annotator]
            for chart_id in mentions:
                mappings[chart_id]['mentions'][annotator] = mentions[chart_id]
        return mappings

    def columns(self) -> list:
        """
        :return: column headers for CSV/SQL
        """
        return ['chart', 'annotator', 'label', 'encounter_ref']

    def to_csv(self) -> list:
        """
        :return: list, each row is "chart, annotator, label, encounter_ref"
        """
        merged = self.merge_ids_and_mentions()
        rows = list()

        for chart_id in merged.keys():
            encounter_ref = merged[chart_id]['encounter_ref']
            for annotator in merged[chart_id]['mentions'].keys():
                labels = merged[chart_id]['mentions'][annotator]

                if 'Encounter/' not in encounter_ref:
                    encounter_ref = 'Encounter/' + encounter_ref

                if not labels:
                    rows.append(f"'{chart_id}','{annotator}','','{encounter_ref}'")
                else:
                    for label in labels:
                        rows.append(f"'{chart_id}','{annotator}','{label}','{encounter_ref}'")
        return rows

    def to_csv_file(self, filepath) -> None:
        """
        :return: to_csv file
        """
        out = self.columns() + self.to_csv()
        out = '\n'.join(out)
        common.write_text(filepath, out)

    def to_sql(self, view='chart_review_mentions') -> str:
        """
        :param view: name of the  
        :return: 
        """
        as_sql = list()

        for row in self.to_csv():
            as_sql.append(f"({row})")

        ctas = f'create or replace view {view} as select * from ( values \n'
        schema = ','.join(self.columns())
        schema = f") \n AS t ({schema}) ;"

        return ctas + '\n,'.join(as_sql) + schema

    def test_sql(self):
        print(self.to_sql('suicide_icd10__psm_notes_balanced_oct26_mentions_jan22'))


if __name__ == '__main__':
    unittest.main()
